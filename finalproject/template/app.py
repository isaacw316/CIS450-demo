# This Flask app acts like a small browser-based photo editor. Users can upload
# an image, preview it beside a processed version, and adjust live filter
# controls like brightness, contrast, blur, sepia, glow, and effect modes.
#
# final project example template
#
# to build:   docker build -t app .
# to run:     docker run -p 80:80 app
# in browser: http://localhost

from flask import Flask, jsonify, request, render_template_string, send_file
import os
import cv2
import socket
import numpy as np
import shutil

app = Flask(__name__)

hostname = socket.gethostname()
UPLOAD_FOLDER = os.path.join(app.root_path, "static")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

DEFAULT_SETTINGS = {
    "threshold": 110,
    "brightness": 0,
    "contrast": 100,
    "saturation": 100,
    "blur": 0,
    "sepia": 0,
    "vignette": 0,
    "glow": 0,
    "sketch": 0,
    "mode": "none",
}
CURRENT_SETTINGS = DEFAULT_SETTINGS.copy()

# I used AI to help me build the UI below
HTML = """
<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>SkyLab Photo FX</title>
    <style>
        :root {
            --bg-top: #dff4ff;
            --bg-bottom: #8ed3ff;
            --panel: rgba(244, 251, 255, 0.84);
            --panel-strong: rgba(255, 255, 255, 0.9);
            --line: rgba(33, 85, 136, 0.14);
            --text: #10314d;
            --muted: #58708a;
            --accent: #1d8fe3;
            --accent-deep: #0b6eb7;
            --shadow: 0 22px 60px rgba(13, 87, 146, 0.16);
        }

        * { box-sizing: border-box; }

        body {
            margin: 0;
            min-height: 100vh;
            font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
            color: var(--text);
            background:
                radial-gradient(circle at top left, rgba(255, 255, 255, 0.72), transparent 28%),
                radial-gradient(circle at 85% 10%, rgba(126, 208, 255, 0.55), transparent 24%),
                linear-gradient(180deg, var(--bg-top) 0%, #bce8ff 42%, var(--bg-bottom) 100%);
            padding: 28px 16px 42px;
        }

        .app-shell {
            max-width: 1280px;
            margin: 0 auto;
        }

        .hero {
            display: grid;
            grid-template-columns: 1.05fr 0.95fr;
            gap: 24px;
            align-items: start;
        }

        .panel {
            background: var(--panel);
            border: 1px solid var(--line);
            border-radius: 28px;
            box-shadow: var(--shadow);
            backdrop-filter: blur(16px);
        }

        .intro {
            padding: 30px;
        }

        .badge {
            display: inline-flex;
            align-items: center;
            padding: 9px 14px;
            border-radius: 999px;
            background: rgba(29, 143, 227, 0.12);
            color: var(--accent-deep);
            font-size: 0.92rem;
            font-weight: 700;
            letter-spacing: 0.02em;
        }

        h1 {
            margin: 16px 0 10px;
            font-size: clamp(2.5rem, 6vw, 4.9rem);
            line-height: 0.92;
            letter-spacing: -0.05em;
        }

        .lead {
            margin: 0;
            max-width: 60ch;
            color: var(--muted);
            line-height: 1.75;
            font-size: 1.04rem;
        }

        .stats {
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 14px;
            margin-top: 24px;
        }

        .stat {
            padding: 18px;
            border-radius: 22px;
            background: rgba(255, 255, 255, 0.6);
            border: 1px solid rgba(33, 85, 136, 0.08);
        }

        .stat strong {
            display: block;
            font-size: 1.28rem;
            margin-bottom: 5px;
        }

        .stat span {
            color: var(--muted);
            font-size: 0.93rem;
        }

        .editor {
            padding: 26px;
            background: var(--panel-strong);
        }

        .editor h2 {
            margin: 0 0 8px;
            font-size: 1.5rem;
        }

        .editor p {
            margin: 0 0 18px;
            color: var(--muted);
            line-height: 1.6;
        }

        form {
            display: grid;
            gap: 18px;
        }

        .field label {
            display: block;
            margin-bottom: 8px;
            font-weight: 700;
        }

        .upload {
            position: relative;
            min-height: 138px;
            display: grid;
            place-items: center;
            border-radius: 24px;
            border: 2px dashed rgba(29, 143, 227, 0.35);
            background: linear-gradient(180deg, rgba(255,255,255,0.94), rgba(227, 245, 255, 0.92));
            text-align: center;
            overflow: hidden;
        }

        .upload input[type="file"] {
            position: absolute;
            inset: 0;
            opacity: 0;
            cursor: pointer;
        }

        .upload strong {
            display: block;
            margin-bottom: 6px;
        }

        .upload span {
            color: var(--muted);
        }

        .mode-select {
            width: 100%;
            padding: 14px 16px;
            border-radius: 16px;
            border: 1px solid rgba(33, 85, 136, 0.14);
            background: rgba(255, 255, 255, 0.78);
            color: var(--text);
            font-size: 0.98rem;
        }

        .slider-grid {
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 14px;
        }

        .slider-card {
            padding: 16px;
            border-radius: 20px;
            background: rgba(255, 255, 255, 0.74);
            border: 1px solid rgba(33, 85, 136, 0.08);
        }

        .slider-head {
            display: flex;
            justify-content: space-between;
            gap: 10px;
            align-items: center;
            margin-bottom: 10px;
        }

        .slider-head label {
            margin: 0;
        }

        .value-pill {
            min-width: 54px;
            text-align: center;
            padding: 6px 10px;
            border-radius: 999px;
            background: rgba(29, 143, 227, 0.12);
            color: var(--accent-deep);
            font-weight: 700;
            font-size: 0.9rem;
        }

        input[type="range"] {
            width: 100%;
            accent-color: var(--accent);
        }

        .actions {
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
        }

        .status {
            min-height: 22px;
            color: var(--accent-deep);
            font-size: 0.93rem;
            font-weight: 600;
        }

        button,
        .ghost {
            border-radius: 999px;
            padding: 14px 22px;
            font-weight: 700;
            font-size: 0.97rem;
            text-decoration: none;
        }

        button {
            border: 0;
            cursor: pointer;
            color: #fff;
            background: linear-gradient(135deg, #26a0f2, #0b6eb7);
            box-shadow: 0 18px 34px rgba(13, 110, 183, 0.24);
        }

        .ghost {
            display: inline-flex;
            align-items: center;
            color: var(--text);
            background: rgba(255, 255, 255, 0.72);
            border: 1px solid rgba(33, 85, 136, 0.12);
        }

        .gallery {
            margin-top: 26px;
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 24px;
        }

        .image-card {
            padding: 18px;
        }

        .image-card h3 {
            margin: 0 0 12px;
            font-size: 1.05rem;
        }

        .frame {
            min-height: 360px;
            display: grid;
            place-items: center;
            overflow: hidden;
            border-radius: 22px;
            background:
                linear-gradient(180deg, rgba(255, 255, 255, 0.86), rgba(223, 244, 255, 0.92));
            border: 1px solid rgba(33, 85, 136, 0.08);
        }

        .frame img {
            width: 100%;
            height: 100%;
            object-fit: contain;
            display: block;
        }

        .empty {
            padding: 50px 24px;
            text-align: center;
            color: var(--muted);
            line-height: 1.7;
        }

        .tips {
            margin-top: 16px;
            padding: 16px 18px;
            border-radius: 18px;
            background: rgba(12, 121, 196, 0.08);
            color: var(--muted);
            line-height: 1.65;
        }

        @media (max-width: 1024px) {
            .hero,
            .gallery,
            .stats,
            .slider-grid {
                grid-template-columns: 1fr;
            }

            .intro,
            .editor {
                padding: 22px;
            }
        }
    </style>
</head>
<body>
    <main class="app-shell">
        <section class="hero">
            <div class="panel intro">
                <div class="badge">Sky Blue Photo Lab</div>
                <h1>SkyLab<br>Photo FX</h1>
                <p class="lead">
                    Turn your Flask demo into a creative image playground. Upload a photo, push the sliders,
                    and mix practical edits with fun Photoshop-style effects like comic ink, dreamy haze,
                    neon glow, and vintage film. Running on <strong>{{ hostname }}</strong>.
                </p>

                <div class="stats">
                    <div class="stat">
                        <strong>{{ settings.mode|title }}</strong>
                        <span>Current effect mode</span>
                    </div>
                    <div class="stat">
                        <strong>{{ settings.threshold }}</strong>
                        <span>Edge sensitivity</span>
                    </div>
                    <div class="stat">
                        <strong>8 sliders</strong>
                        <span>Creative adjustments ready to mix</span>
                    </div>
                </div>

                <div class="tips">
                    Try <strong>Neon Pop</strong> with higher glow and sketch, or <strong>Dream Haze</strong>
                    with blur, saturation, and vignette for a softer cinematic look.
                </div>
            </div>

            <div class="panel editor">
                <h2>Creative Controls</h2>
                <p>Each slider is functional, and the style mode changes the final effect recipe before the image is saved.</p>

                <form id="editor-form" method="POST" action="/edges" enctype="multipart/form-data">
                    <div class="field">
                        <label for="file">Image Upload</label>
                        <div class="upload">
                            <input id="file" type="file" name="file" accept="image/*">
                            <div>
                                <strong>Drop a photo here or click to browse</strong>
                                <span>Upload a new image any time to test different looks</span>
                            </div>
                        </div>
                    </div>

                    <div class="field">
                        <label for="mode">Effect Mode</label>
                        <select class="mode-select" id="mode" name="mode">
                            {% for mode_value, mode_label in modes %}
                                <option value="{{ mode_value }}" {% if settings.mode == mode_value %}selected{% endif %}>{{ mode_label }}</option>
                            {% endfor %}
                        </select>
                    </div>

                    <div class="slider-grid">
                        {% for slider in sliders %}
                            <div class="slider-card">
                                <div class="slider-head">
                                    <label for="{{ slider.id }}">{{ slider.label }}</label>
                                    <div class="value-pill"><span id="{{ slider.id }}-value">{{ settings[slider.id] }}</span></div>
                                </div>
                                <input
                                    id="{{ slider.id }}"
                                    type="range"
                                    name="{{ slider.id }}"
                                    min="{{ slider.min }}"
                                    max="{{ slider.max }}"
                                    step="{{ slider.step }}"
                                    value="{{ settings[slider.id] }}"
                                    oninput="document.getElementById('{{ slider.id }}-value').textContent = this.value"
                                >
                            </div>
                        {% endfor %}
                    </div>

                    <div class="actions">
                        <a class="ghost" href="/download">Download Image</a>
                        <button type="button" class="ghost" id="reset-button">Reset Controls</button>
                    </div>
                    <div class="status" id="status-text"></div>
                </form>
            </div>
        </section>

        <section class="gallery">
            <article class="panel image-card">
                <h3>Original Image</h3>
                <div class="frame">
                    {% if original %}
                        <img id="original-preview" src="{{ original }}" alt="Original uploaded image">
                    {% else %}
                        <div class="empty" id="original-empty">Upload an image to start building a custom look.</div>
                    {% endif %}
                </div>
            </article>

            <article class="panel image-card">
                <h3>Processed Output</h3>
                <div class="frame">
                    {% if processed %}
                        <img id="processed-preview" src="{{ processed }}" alt="Processed image with creative filters">
                    {% else %}
                        <div class="empty" id="processed-empty">Your filtered result will appear here after you render the image.</div>
                    {% endif %}
                </div>
            </article>
        </section>
    </main>
    <script>
        const form = document.getElementById("editor-form");
        const fileInput = document.getElementById("file");
        const modeSelect = document.getElementById("mode");
        const resetButton = document.getElementById("reset-button");
        const statusText = document.getElementById("status-text");
        const originalFrame = document.querySelector(".gallery .image-card:first-child .frame");
        const processedFrame = document.querySelector(".gallery .image-card:last-child .frame");
        const sliders = Array.from(document.querySelectorAll('input[type="range"]'));
        let previewTimer = null;
        let previewController = null;

        function setStatus(message) {
            statusText.textContent = message || "";
        }

        function ensurePreviewImage(frame, imageId, altText) {
            let imageEl = document.getElementById(imageId);
            if (imageEl) return imageEl;

            const emptyState = frame.querySelector(".empty");
            if (emptyState) {
                emptyState.remove();
            }

            imageEl = document.createElement("img");
            imageEl.id = imageId;
            imageEl.alt = altText;
            frame.appendChild(imageEl);
            return imageEl;
        }

        function refreshImage(frame, imageId, altText, src) {
            if (!src) return;
            const imageEl = ensurePreviewImage(frame, imageId, altText);
            imageEl.src = src + "?t=" + Date.now();
        }

        function updatePreviewState(payload) {
            if (payload.original) {
                refreshImage(originalFrame, "original-preview", "Original uploaded image", payload.original);
            }
            if (payload.processed) {
                refreshImage(processedFrame, "processed-preview", "Processed image with creative filters", payload.processed);
            }
            if (payload.status) {
                setStatus(payload.status);
            }
        }

        function buildSettingsFormData() {
            const formData = new FormData();
            sliders.forEach((slider) => {
                formData.append(slider.name, slider.value);
            });
            formData.append("mode", modeSelect.value);
            return formData;
        }

        async function postForm(url, body, controller) {
            const response = await fetch(url, {
                method: "POST",
                body,
                signal: controller ? controller.signal : undefined
            });
            if (!response.ok) {
                throw new Error("Request failed");
            }
            return response.json();
        }

        function schedulePreview() {
            clearTimeout(previewTimer);
            previewTimer = setTimeout(async () => {
                setStatus("Updating preview...");
                if (previewController) {
                    previewController.abort();
                }
                previewController = new AbortController();
                try {
                    const payload = await postForm("/preview", buildSettingsFormData(), previewController);
                    updatePreviewState(payload);
                } catch (error) {
                    if (error.name !== "AbortError") {
                        setStatus("Preview update failed.");
                    }
                } finally {
                    previewController = null;
                }
            }, 180);
        }

        sliders.forEach((slider) => {
            slider.addEventListener("input", schedulePreview);
        });

        modeSelect.addEventListener("change", schedulePreview);

        fileInput.addEventListener("change", async () => {
            if (!fileInput.files.length) return;
            setStatus("Uploading image...");
            try {
                const uploadData = new FormData();
                uploadData.append("file", fileInput.files[0]);
                const payload = await postForm("/upload", uploadData);
                updatePreviewState(payload);
                sliders.forEach((slider) => {
                    slider.value = payload.settings[slider.name];
                    document.getElementById(slider.id + "-value").textContent = slider.value;
                });
                modeSelect.value = payload.settings.mode;
            } catch (error) {
                setStatus("Upload failed.");
            }
        });

        resetButton.addEventListener("click", async () => {
            setStatus("Resetting controls...");
            try {
                const payload = await postForm("/reset", new FormData());
                updatePreviewState(payload);
                sliders.forEach((slider) => {
                    slider.value = payload.settings[slider.name];
                    document.getElementById(slider.id + "-value").textContent = slider.value;
                });
                modeSelect.value = payload.settings.mode;
            } catch (error) {
                setStatus("Reset failed.");
            }
        });

        form.addEventListener("submit", async (event) => {
            event.preventDefault();
            setStatus("Rendering effect...");
            try {
                const payload = await postForm("/preview", buildSettingsFormData());
                updatePreviewState(payload);
            } catch (error) {
                setStatus("Render failed.");
            }
        });
    </script>
</body>
</html>
"""
#AI gave me the ideas for some of the sliders, such as sepia and vignette
SLIDERS = [
    {"id": "threshold", "label": "Edge Threshold", "min": 20, "max": 255, "step": 1},
    {"id": "brightness", "label": "Brightness", "min": -100, "max": 100, "step": 1},
    {"id": "contrast", "label": "Contrast", "min": 50, "max": 180, "step": 1},
    {"id": "saturation", "label": "Saturation", "min": 0, "max": 200, "step": 1},
    # The blur slider softens the image by averaging nearby pixels more strongly
    # as the slider value increases.
    {"id": "blur", "label": "Blur", "min": 0, "max": 20, "step": 1},
    {"id": "sepia", "label": "Sepia", "min": 0, "max": 100, "step": 1},
    {"id": "vignette", "label": "Vignette", "min": 0, "max": 100, "step": 1},
    {"id": "glow", "label": "Glow", "min": 0, "max": 100, "step": 1},
    {"id": "sketch", "label": "Sketch Blend", "min": 0, "max": 100, "step": 1},
]

MODE_OPTIONS = [
    ("none", "Clean Studio"),
    ("comic", "Comic Ink"),
    ("dream", "Dream Haze"),
    ("neon", "Neon Pop"),
    ("vintage", "Vintage Film"),
]


def clamp(value, low, high):
    # Keeps a number inside a safe minimum/maximum range so filter math does not
    # go outside the values the app expects.
    return max(low, min(high, value))


def odd_kernel(value):
    # AI says it converts a blur amount into an odd kernel size because Gaussian blur in
    # OpenCV requires odd-numbered kernel dimensions.
    value = max(0, int(value))
    if value == 0:
        return 0
    return value if value % 2 == 1 else value + 1


def blend_images(base, overlay, amount):
    # Mixes two images together using a percentage so effect layers can be
    # gently or strongly blended onto the original image.
    alpha = clamp(amount / 100.0, 0.0, 1.0)
    return cv2.addWeighted(base, 1.0 - alpha, overlay, alpha, 0)


def apply_sepia(img, amount):
    # Creates a warm sepia-toned version of the image and blends it back in
    # based on the requested sepia slider strength.
    if amount <= 0:
        return img
    sepia_matrix = np.array(
        [
            [0.131, 0.534, 0.272],
            [0.168, 0.686, 0.349],
            [0.189, 0.769, 0.393],
        ],
        dtype=np.float32,
    )
    transformed = cv2.transform(img.astype(np.float32), sepia_matrix)
    transformed = np.clip(transformed, 0, 255).astype(np.uint8)
    return blend_images(img, transformed, amount)


def apply_vignette(img, amount):
    # Darkens the edges of the image with a radial mask to create a vignette
    # effect, with stronger darkening at higher slider values.
    if amount <= 0:
        return img
    rows, cols = img.shape[:2]
    sigma_x = max(cols / 1.8, 1)
    sigma_y = max(rows / 1.8, 1)
    kernel_x = cv2.getGaussianKernel(cols, sigma_x)
    kernel_y = cv2.getGaussianKernel(rows, sigma_y)
    mask = kernel_y @ kernel_x.T
    mask = mask / mask.max()
    strength = 1.0 - (amount / 100.0) * 0.72
    mask = strength + (1.0 - strength) * mask
    return np.clip(img.astype(np.float32) * mask[:, :, np.newaxis], 0, 255).astype(np.uint8)


def apply_sketch_overlay(img, amount):
    # Builds a pencil-sketch style layer from grayscale edges and blends it
    # over the photo for a hand-drawn look.
    if amount <= 0:
        return img
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    inverted = 255 - gray
    blur = cv2.GaussianBlur(inverted, (21, 21), 0)
    sketch = cv2.divide(gray, 255 - blur, scale=256.0)
    sketch_bgr = cv2.cvtColor(sketch, cv2.COLOR_GRAY2BGR)
    return blend_images(img, sketch_bgr, amount)


def apply_edge_glow(img, threshold, amount, color=(255, 235, 120)):
    # Detects edges with Canny, colors those edges, and blends them over the
    # image to create a glowing-outline effect.
    if amount <= 0:
        return img
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, max(10, threshold // 2), threshold)
    edges = cv2.GaussianBlur(edges, (3, 3), 0)
    overlay = np.zeros_like(img)
    overlay[edges > 0] = color
    return blend_images(img, overlay, amount)


def apply_edge_overlay(img, threshold):
    # Uses the threshold slider to create a visible edge-ink effect even in the
    # default mode, so moving the threshold control updates the preview on its own.
    difference = abs(threshold - DEFAULT_SETTINGS["threshold"])
    if difference == 0:
        return img

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    edges = cv2.Canny(gray, max(10, threshold // 2), threshold)
    edges_bgr = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    inverted_edges = 255 - edges_bgr
    amount = clamp(difference * 0.8, 0, 55)
    return blend_images(img, inverted_edges, amount)


def apply_mode(img, mode, threshold):
    # Applies one of the preset creative looks before the manual sliders are
    # layered on, such as comic, dream, neon, or vintage.
    if mode == "comic":
        smooth = cv2.bilateralFilter(img, 9, 60, 60)
        gray = cv2.cvtColor(smooth, cv2.COLOR_BGR2GRAY)
        ink = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 7)
        ink = cv2.cvtColor(ink, cv2.COLOR_GRAY2BGR)
        comic = cv2.bitwise_and(smooth, ink)
        return blend_images(img, comic, 70)

    if mode == "dream":
        glow = cv2.GaussianBlur(img, (0, 0), 8)
        dreamy = cv2.addWeighted(img, 0.72, glow, 0.52, 8)
        return apply_vignette(dreamy, 20)

    if mode == "neon":
        hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 1.55, 0, 255)
        hsv[:, :, 2] = np.clip(hsv[:, :, 2] * 1.1, 0, 255)
        neon = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        return apply_edge_glow(neon, threshold, 65, color=(255, 255, 0))

    if mode == "vintage":
        vintage = apply_sepia(img, 45)
        hsv = cv2.cvtColor(vintage, cv2.COLOR_BGR2HSV).astype(np.float32)
        hsv[:, :, 1] = np.clip(hsv[:, :, 1] * 0.78, 0, 255)
        vintage = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)
        return apply_vignette(vintage, 32)

    return img


def process_image(input_path, output_path, settings):
    # Loads the uploaded image, applies the selected preset mode plus all slider
    # adjustments, and writes the final processed result to disk.
    img = cv2.imread(input_path)
    if img is None:
        raise ValueError("Uploaded image could not be read.")

    img = apply_mode(img, settings["mode"], settings["threshold"])

    contrast = settings["contrast"] / 100.0
    brightness = settings["brightness"]
    adjusted = img.astype(np.float32) * contrast + brightness
    img = np.clip(adjusted, 0, 255).astype(np.uint8)

    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV).astype(np.float32)
    hsv[:, :, 1] = np.clip(hsv[:, :, 1] * (settings["saturation"] / 100.0), 0, 255)
    img = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2BGR)

    if settings["blur"] > 0:
        # Uses a larger kernel and sigma value so the blur slider creates a
        # clearly visible soft-focus effect as the user increases it.
        kernel = odd_kernel(settings["blur"] * 2 + 1)
        sigma = max(settings["blur"] / 2.0, 0.1)
        img = cv2.GaussianBlur(img, (kernel, kernel), sigmaX=sigma, sigmaY=sigma)

    img = apply_sepia(img, settings["sepia"])

    if settings["glow"] > 0:
        soft = cv2.GaussianBlur(img, (0, 0), 6)
        img = blend_images(img, soft, settings["glow"])

    img = apply_edge_overlay(img, settings["threshold"])
    img = apply_vignette(img, settings["vignette"])
    img = apply_sketch_overlay(img, settings["sketch"])
    if settings["glow"] > 0:
        img = apply_edge_glow(img, settings["threshold"], settings["glow"] // 2)

    cv2.imwrite(output_path, img)
    return output_path


def current_image_paths():
    # Returns the browser paths for the original and processed images only if
    # those files already exist in the static folder.
    original = os.path.join(UPLOAD_FOLDER, "original.jpg")
    output = os.path.join(UPLOAD_FOLDER, "output.jpg")
    return (
        "/static/original.jpg" if os.path.exists(original) else None,
        "/static/output.jpg" if os.path.exists(output) else None,
    )


def original_path():
    # Provides the filesystem path where the uploaded original image is stored.
    return os.path.join(UPLOAD_FOLDER, "original.jpg")


def output_path():
    # Provides the filesystem path where the processed preview image is stored.
    return os.path.join(UPLOAD_FOLDER, "output.jpg")


def save_unmodified_output():
    # Copies the original upload to the output slot so the processed preview can
    # start by showing the untouched image before filters are applied.
    if os.path.exists(original_path()):
        shutil.copyfile(original_path(), output_path())


def settings_from_request():
    # Reads slider and mode values from the submitted form data and returns a
    # validated settings dictionary for the current preview.
    new_settings = DEFAULT_SETTINGS.copy()
    for slider in SLIDERS:
        slider_id = slider["id"]
        new_settings[slider_id] = request.form.get(slider_id, default=new_settings[slider_id], type=int)

    mode = request.form.get("mode", DEFAULT_SETTINGS["mode"], type=str)
    valid_modes = {value for value, _label in MODE_OPTIONS}
    new_settings["mode"] = mode if mode in valid_modes else DEFAULT_SETTINGS["mode"]
    return new_settings


def is_default_settings(settings):
    # Checks whether the current controls are still at their neutral defaults.
    return settings == DEFAULT_SETTINGS


def render_current_output():
    # Updates the processed image on disk using either the untouched original
    # image or the full filter pipeline depending on the current settings.
    if not os.path.exists(original_path()):
        return False
    if is_default_settings(CURRENT_SETTINGS):
        save_unmodified_output()
    else:
        process_image(original_path(), output_path(), CURRENT_SETTINGS)
    return True


def preview_payload(status):
    # Packages the latest image URLs, settings, and status text into a JSON
    # response for the frontend live-preview requests.
    original, processed = current_image_paths()
    return {
        "original": original,
        "processed": processed,
        "settings": CURRENT_SETTINGS,
        "status": status,
    }


def render_page():
    original, processed = current_image_paths()
    return render_template_string(
        HTML,
        hostname=hostname,
        original=original,
        processed=processed,
        settings=CURRENT_SETTINGS,
        sliders=SLIDERS,
        modes=MODE_OPTIONS,
    )


@app.route("/")
def home():
    # Renders the main page with the current image paths and the latest control
    # values shown in the UI.
    return render_page()


@app.route("/edges", methods=["POST"])
def edges_route():
    # Handles the traditional form submission flow: save a new upload if one was
    # provided, update the settings, rebuild the output image, and rerender.
    global CURRENT_SETTINGS
    file = request.files.get("file")
    if file and file.filename:
        file.save(original_path())
        CURRENT_SETTINGS = DEFAULT_SETTINGS.copy()
        save_unmodified_output()

    if not os.path.exists(original_path()):
        return "No image uploaded yet."

    CURRENT_SETTINGS = settings_from_request()
    render_current_output()
    return render_page()


@app.route("/upload", methods=["POST"])
def upload_route():
    # Receives a newly uploaded image from the live UI, stores it, resets the
    # controls to defaults, and returns the untouched preview image.
    global CURRENT_SETTINGS
    file = request.files.get("file")
    if not file or not file.filename:
        return jsonify({"status": "Choose an image first."}), 400

    file.save(original_path())
    CURRENT_SETTINGS = DEFAULT_SETTINGS.copy()
    save_unmodified_output()
    return jsonify(preview_payload("Image uploaded. No effects applied yet."))


@app.route("/preview", methods=["POST"])
def preview_route():
    # Receives live slider updates from the page, regenerates the processed
    # preview image, and returns fresh image URLs as JSON.
    global CURRENT_SETTINGS
    if not os.path.exists(original_path()):
        return jsonify({"status": "Upload an image first."}), 400

    CURRENT_SETTINGS = settings_from_request()
    render_current_output()
    return jsonify(preview_payload("Preview updated."))


@app.route("/reset", methods=["POST"])
def reset_route():
    # Restores all controls to their default values and resets the processed
    # preview back to the original uploaded image.
    global CURRENT_SETTINGS
    CURRENT_SETTINGS = DEFAULT_SETTINGS.copy()
    if not os.path.exists(original_path()):
        return jsonify({"status": "Controls reset."})

    save_unmodified_output()
    return jsonify(preview_payload("Controls reset to the original image."))


@app.route("/download")
def download_route():
    # Sends the current processed image to the browser as a downloadable file.
    if not os.path.exists(output_path()):
        return "No processed image available yet.", 404
    return send_file(output_path(), as_attachment=True, download_name="skylab-photo-fx.jpg")


if __name__ == "__main__":
    # Starts the local Flask development server and exposes it on port 5000
    # unless a different PORT environment variable is set.
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
