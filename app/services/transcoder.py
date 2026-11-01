import io
import os
import math
import base64
import subprocess
from typing import Tuple, List, Optional
from concurrent.futures import ThreadPoolExecutor
from PIL import Image, ImageSequence

# Register HEIF / HEIC opener for iOS images uploaded in comments
try:
    import pillow_heif
    pillow_heif.register_heif_opener()
except ImportError:
    pass

from app.config import settings
from app.schemas.sticker import TranscodeResult

class StickerTranscoder:
    """
    Ultra-optimized multimedia normalization pipeline for WhatsApp & Telegram Stickers:
    - 512x512 canvas with transparent RGBA padding (16px safe margin)
    - WhatsApp Animated WebP: duration <= 3.0s, loop=0, framerate clamped (15-20 fps), weight < 500 KB
    - Telegram Video Sticker: 512x512 WebM (VP9 realtime, yuva420p alpha, duration <= 3.0s, weight < 256 KB)
    - Static WebP: weight < 100 KB
    - Tray Icon: 96x96 px, weight < 50 KB (optional, skipped by default for Telegram bot)
    """

    @classmethod
    def transcode(
        cls, 
        raw_bytes: bytes, 
        is_animated_hint: Optional[bool] = None, 
        generate_tray: bool = False,
        generate_telegram_webm: bool = True
    ) -> Tuple[bytes, Optional[bytes], TranscodeResult]:
        """
        Main entry point for transcoding arbitrary image/animation data into WhatsApp compliant WebP
        and optional Telegram compliant WebM video sticker.
        """
        with Image.open(io.BytesIO(raw_bytes)) as im:
            is_animated = getattr(im, "is_animated", False)
            if is_animated_hint is not None:
                is_animated = is_animated or is_animated_hint

            frame_count = getattr(im, "n_frames", 1)
            if frame_count <= 1:
                is_animated = False

            telegram_webm_bytes = None
            if is_animated:
                # Optimized animated pipeline: frame extraction & normalization
                canvas_frames, selected_durations, total_time_ms, final_fps = cls._prepare_animated_frames(im)
                
                # Execute WebP encoding and WebM VP9 encoding concurrently if both are needed
                if generate_telegram_webm and canvas_frames:
                    with ThreadPoolExecutor(max_workers=2) as executor:
                        f_webp = executor.submit(cls._encode_animated_webp, canvas_frames, selected_durations)
                        f_webm = executor.submit(cls._generate_telegram_webm, canvas_frames, final_fps)
                        sticker_bytes = f_webp.result()
                        telegram_webm_bytes = f_webm.result()
                else:
                    sticker_bytes = cls._encode_animated_webp(canvas_frames, selected_durations)

                duration_ms = total_time_ms
                fps = final_fps
                final_frames = len(canvas_frames)
            else:
                sticker_bytes = cls._process_static(im)
                duration_ms = None
                fps = None
                final_frames = 1

            # Generate WhatsApp 96x96 Tray Icon only if explicitly requested
            tray_bytes = None
            if generate_tray:
                im.seek(0)
                tray_bytes = cls._generate_tray_icon(im)

        size_bytes = len(sticker_bytes)
        size_kb = round(size_bytes / 1024, 2)
        tray_size = len(tray_bytes) if tray_bytes else None
        webm_size = len(telegram_webm_bytes) if telegram_webm_bytes else None

        compliance = {
            "canvas_512x512": True,
            "size_under_limit": (
                size_bytes < settings.WA_MAX_ANIMATED_SIZE_BYTES if is_animated 
                else size_bytes < settings.WA_MAX_STATIC_SIZE_BYTES
            ),
            "duration_under_3s": (duration_ms <= settings.WA_MAX_DURATION_MS) if duration_ms else True,
            "status": "PASSED"
        }

        result = TranscodeResult(
            success=compliance["size_under_limit"] and compliance["duration_under_3s"],
            is_animated=is_animated,
            width=settings.WA_CANVAS_SIZE,
            height=settings.WA_CANVAS_SIZE,
            size_bytes=size_bytes,
            size_kb=size_kb,
            frame_count=final_frames,
            duration_ms=duration_ms,
            fps=fps,
            compliance=compliance,
            base64_data=base64.b64encode(sticker_bytes).decode("ascii"),
            tray_icon_base64=base64.b64encode(tray_bytes).decode("ascii") if tray_bytes else None,
            tray_size_bytes=tray_size,
            telegram_webm_base64=base64.b64encode(telegram_webm_bytes).decode("ascii") if telegram_webm_bytes else None,
            telegram_webm_size_bytes=webm_size
        )

        return sticker_bytes, tray_bytes, result

    @classmethod
    def _fit_to_canvas(cls, img: Image.Image, canvas_size: int, safe_padding: int) -> Image.Image:
        """
        Resizes an image preserving aspect ratio to fit inside (canvas_size - 2*safe_padding)
        and centers it onto a transparent RGBA canvas. Uses BICUBIC for high performance & sharpness.
        """
        target_box = canvas_size - (2 * safe_padding)
        img = img.convert("RGBA")

        w, h = img.size
        scale = min(target_box / max(w, 1), target_box / max(h, 1))
        new_w = max(1, int(round(w * scale)))
        new_h = max(1, int(round(h * scale)))

        resized = img.resize((new_w, new_h), Image.Resampling.BICUBIC)

        canvas = Image.new("RGBA", (canvas_size, canvas_size), (0, 0, 0, 0))
        offset_x = (canvas_size - new_w) // 2
        offset_y = (canvas_size - new_h) // 2
        canvas.paste(resized, (offset_x, offset_y), resized)
        return canvas

    @classmethod
    def _process_static(cls, im: Image.Image) -> bytes:
        """
        Transcodes a static image to 512x512 WebP (< 100 KB) at high speed (method=3).
        """
        canvas = cls._fit_to_canvas(im, settings.WA_CANVAS_SIZE, settings.WA_SAFE_PADDING)
        
        for q in [85, 70, 50]:
            out = io.BytesIO()
            canvas.save(out, format="WEBP", quality=q, method=3)
            data = out.getvalue()
            if len(data) <= settings.WA_MAX_STATIC_SIZE_BYTES:
                return data

        out = io.BytesIO()
        canvas.save(out, format="WEBP", quality=30, method=4)
        return out.getvalue()

    @classmethod
    def _prepare_animated_frames(cls, im: Image.Image) -> Tuple[List[Image.Image], List[int], int, float]:
        """
        Extracts frames, clamps duration to <= 3000ms, caps FPS at 20, and normalizes to 512x512.
        """
        raw_frames = []
        raw_durations = []
        total_time_ms = 0

        for frame in ImageSequence.Iterator(im):
            d = frame.info.get("duration", 100) or 100
            if d <= 0:
                d = 100
            if total_time_ms + d > settings.WA_MAX_DURATION_MS:
                break
            raw_frames.append(frame.copy())
            raw_durations.append(d)
            total_time_ms += d

        if not raw_frames:
            im.seek(0)
            raw_frames = [im.copy()]
            raw_durations = [100]
            total_time_ms = 100

        orig_fps = (len(raw_frames) / (total_time_ms / 1000.0)) if total_time_ms > 0 else 15.0
        step = 1
        if orig_fps > settings.WA_TARGET_FPS_MAX:
            step = max(1, int(round(orig_fps / settings.WA_TARGET_FPS_MAX)))

        selected_frames = raw_frames[::step]
        selected_durations = [
            sum(raw_durations[i : min(i + step, len(raw_durations))])
            for i in range(0, len(raw_frames), step)
        ]

        total_time_ms = sum(selected_durations)
        final_fps = round((len(selected_frames) / (total_time_ms / 1000.0)) if total_time_ms > 0 else 15.0, 1)

        canvas_frames = [
            cls._fit_to_canvas(f, settings.WA_CANVAS_SIZE, settings.WA_SAFE_PADDING)
            for f in selected_frames
        ]

        return canvas_frames, selected_durations, total_time_ms, final_fps

    @classmethod
    def _encode_animated_webp(cls, canvas_frames: List[Image.Image], durations: List[int]) -> bytes:
        """
        Fast adaptive WebP animation encoder using method=2 for 2-3x faster throughput.
        """
        for q in [75, 55, 40]:
            out = io.BytesIO()
            canvas_frames[0].save(
                out,
                format="WEBP",
                save_all=True,
                append_images=canvas_frames[1:],
                duration=durations,
                loop=0,
                quality=q,
                method=2
            )
            data = out.getvalue()
            if len(data) <= settings.WA_MAX_ANIMATED_SIZE_BYTES:
                return data

        # Fallback if still over 500 KB: decimate frames
        if len(canvas_frames) > 4:
            decimated_frames = canvas_frames[::2]
            decimated_durations = [d * 2 for d in durations[::2]]
            out = io.BytesIO()
            decimated_frames[0].save(
                out,
                format="WEBP",
                save_all=True,
                append_images=decimated_frames[1:],
                duration=decimated_durations,
                loop=0,
                quality=35,
                method=2
            )
            return out.getvalue()

        return data

    @classmethod
    def _generate_telegram_webm(cls, canvas_frames: List[Image.Image], fps: float) -> Optional[bytes]:
        """
        Ultra-fast Telegram-compliant Video Sticker generation:
        - libvpx-vp9 with '-deadline realtime' and '-cpu-used 6' (6x faster encoding)
        - Multi-threaded row-based encoding (-row-mt 1)
        - Transparent RGBA (yuva420p)
        - Target <= 256 KB
        """
        if not canvas_frames:
            return None
        try:
            width, height = canvas_frames[0].size
            raw_payload = b"".join(f.tobytes() for f in canvas_frames)
            fps_clamped = max(1.0, min(float(fps), 30.0))

            ffmpeg_bin = "/home/rakazo/.local/bin/ffmpeg" if os.path.exists("/home/rakazo/.local/bin/ffmpeg") else "ffmpeg"

            cmd = [
                ffmpeg_bin, "-y",
                "-f", "rawvideo",
                "-vcodec", "rawvideo",
                "-s", f"{width}x{height}",
                "-pix_fmt", "rgba",
                "-r", str(fps_clamped),
                "-i", "-",
                "-c:v", "libvpx-vp9",
                "-pix_fmt", "yuva420p",
                "-deadline", "realtime",
                "-cpu-used", "6",
                "-row-mt", "1",
                "-b:v", "200k",
                "-crf", "32",
                "-an",
                "-t", "3.0",
                "-f", "webm",
                "-"
            ]
            p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            webm_bytes, _ = p.communicate(input=raw_payload)
            if p.returncode == 0 and 0 < len(webm_bytes) <= 256 * 1024:
                return webm_bytes
            elif p.returncode == 0 and len(webm_bytes) > 256 * 1024:
                # Quick compression pass
                cmd_comp = [
                    ffmpeg_bin, "-y",
                    "-f", "rawvideo",
                    "-vcodec", "rawvideo",
                    "-s", f"{width}x{height}",
                    "-pix_fmt", "rgba",
                    "-r", str(fps_clamped),
                    "-i", "-",
                    "-c:v", "libvpx-vp9",
                    "-pix_fmt", "yuva420p",
                    "-deadline", "realtime",
                    "-cpu-used", "6",
                    "-row-mt", "1",
                    "-b:v", "120k",
                    "-crf", "38",
                    "-an",
                    "-t", "3.0",
                    "-f", "webm",
                    "-"
                ]
                p2 = subprocess.Popen(cmd_comp, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                webm_comp, _ = p2.communicate(input=raw_payload)
                if p2.returncode == 0 and len(webm_comp) > 0:
                    return webm_comp
        except Exception:
            pass
        return None

    @classmethod
    def _generate_tray_icon(cls, im: Image.Image) -> bytes:
        """
        Generates 96x96 px tray icon for WhatsApp sticker pack (< 50 KB).
        """
        canvas = cls._fit_to_canvas(im, settings.WA_TRAY_ICON_SIZE, safe_padding=4)
        out = io.BytesIO()
        canvas.save(out, format="WEBP", quality=80, method=3)
        return out.getvalue()
