# import os
# import subprocess
# import csv
# import random
# import textwrap

# # === Folder paths ===
# TEXT_FOLDER = './text'
# TIMING_FOLDER = './timing'
# GIF_FOLDER = './gif'  # Top half
# BOTTOM_VIDEO_FOLDER = './bottom_video'  # Bottom half
# AUDIO_FOLDER = './audio'
# MUSIC_FOLDER = './music'
# OUTPUT_FOLDER = './output_video'
# TEMP_FOLDER = './temp_resized'
# FONT_PATH = './Roboto-ExtraBold.ttf'

# os.makedirs(OUTPUT_FOLDER, exist_ok=True)
# os.makedirs(TEMP_FOLDER, exist_ok=True)

# for filename in os.listdir(TEXT_FOLDER):
#     if filename.endswith('.txt'):
#         base_name = os.path.splitext(filename)[0]

#         text_path = os.path.join(TEXT_FOLDER, filename)
#         timing_path = os.path.join(TIMING_FOLDER, base_name + '.csv')
#         top_video_path = os.path.join(GIF_FOLDER, base_name + '.mp4')
#         bottom_video_path = os.path.join(BOTTOM_VIDEO_FOLDER, base_name + '.mp4')
#         audio_path = os.path.join(AUDIO_FOLDER, base_name + '.mp3')

#         resized_top = os.path.join(TEMP_FOLDER, base_name + '_top_resized.mp4')
#         resized_bottom = os.path.join(TEMP_FOLDER, base_name + '_bottom_resized.mp4')

#         # === Resize videos to 1080x960 each ===
#         subprocess.run([
#             'ffmpeg', '-y', '-i', top_video_path,
#             '-vf', 'scale=1080:960:force_original_aspect_ratio=increase,crop=1080:960',
#             '-c:a', 'copy', resized_top
#         ], check=True)

#         subprocess.run([
#             'ffmpeg', '-y', '-i', bottom_video_path,
#             '-vf', 'scale=1080:960:force_original_aspect_ratio=increase,crop=1080:960',
#             '-c:a', 'copy', resized_bottom
#         ], check=True)


#         # === Pick random music ===
#         music_files = [f for f in os.listdir(MUSIC_FOLDER) if f.endswith('.mp3')]
#         music_path = os.path.join(MUSIC_FOLDER, random.choice(music_files)) if music_files else None
#         output_path = os.path.join(OUTPUT_FOLDER, base_name + '.mp4')

#         # === Load CSV timings and wrap lines ===
#         timed_texts = []
#         max_chars_per_line = 30
#         line_gap = 0
#         fontsize = 64

#         with open(timing_path, newline='', encoding='utf-8') as csvfile:
#             reader = csv.reader(csvfile)
#             for row in reader:
#                 if len(row) >= 3:
#                     start, end, full_line = float(row[0]), float(row[1]), row[2]
#                     wrapped_lines = textwrap.wrap(full_line, width=max_chars_per_line)
#                     duration_per_line = (end - start) / len(wrapped_lines)
#                     for i, line in enumerate(wrapped_lines):
#                         line_start = start + i * duration_per_line
#                         line_end = line_start + duration_per_line
#                         timed_texts.append((line_start, line_end, line))

#         # === Build drawtext filters ===
#         drawtext_filters = []
#         total_lines = len(timed_texts)
#         for i, (start, end, line) in enumerate(timed_texts):
#             safe_line = line.replace("'", "''")
#             y_position = f"(h/2 - {(total_lines//2 - i) * line_gap})"
#             drawtext_filters.append(
#                 f"drawtext=fontfile='{FONT_PATH}':text='{safe_line}':"
#                 f"fontcolor=#FFD700:fontsize={fontsize + 16}:"
#                 f"box=1:boxcolor=black@0.5:boxborderw=14:"
#                 f"borderw=4:bordercolor=black:"
#                 f"x=(w-text_w)/2:y={y_position}:enable='between(t,{start},{end})'"
#             )


#         stacked_and_text = f"[top][bottom]vstack=inputs=2[stacked];[stacked]{','.join(drawtext_filters)}[v]"
#         filter_complex_parts = [
#             f"[0:v]null[top]",
#             f"[1:v]null[bottom]",
#             stacked_and_text
#         ]
#         filter_complex = ";".join(filter_complex_parts)

#         # === Build final FFmpeg command ===
#         if music_path:
#             cmd = [
#                 'ffmpeg',
#                 '-y',
#                 '-i', resized_top,
#                 '-i', resized_bottom,
#                 '-i', audio_path,
#                 '-i', music_path,
#                 '-filter_complex',
#                 f"{filter_complex};"
#                 f"[2:a]volume=1[a1];"
#                 f"[3:a]volume=0.2[a2];"
#                 f"[a1][a2]amix=inputs=2:duration=first:dropout_transition=2[aout]",
#                 '-map', '[v]',
#                 '-map', '[aout]',
#                 '-c:v', 'libx264',
#                 '-tune', 'stillimage',
#                 '-c:a', 'aac',
#                 '-b:a', '192k',
#                 '-pix_fmt', 'yuv420p',
#                 '-shortest',
#                 output_path
#             ]
#         else:
#             cmd = [
#                 'ffmpeg',
#                 '-y',
#                 '-i', resized_top,
#                 '-i', resized_bottom,
#                 '-i', audio_path,
#                 '-filter_complex',
#                 f"{filter_complex};[2:a]anull[aout]",
#                 '-map', '[v]',
#                 '-map', '[aout]',
#                 '-c:v', 'libx264',
#                 '-c:a', 'aac',
#                 '-b:a', '192k',
#                 '-pix_fmt', 'yuv420p',
#                 '-shortest',
#                 output_path
#             ]

#         print(f"🎬 Generating video for: {base_name}")
#         subprocess.run(cmd, check=True)

# print("✅ All videos generated.")

# import os
# import subprocess
# import random
# import whisperx
# import torch
# import librosa

# # === Folder paths ===
# TEXT_FOLDER = './text'
# AUDIO_FOLDER = './audio'
# GIF_FOLDER = './gif'
# MUSIC_FOLDER = './music'
# OUTPUT_FOLDER = './output_video'
# TEMP_FOLDER = './temp_resized'
# FONT_PATH = './Chewy-Regular.ttf'

# os.makedirs(OUTPUT_FOLDER, exist_ok=True)
# os.makedirs(TEMP_FOLDER, exist_ok=True)

# device = 'cuda' if torch.cuda.is_available() else 'cpu'
# compute_type = "float32"

# # Load WhisperX ASR model once
# model = whisperx.load_model("large-v2", device, compute_type=compute_type)

# for filename in os.listdir(TEXT_FOLDER):
#     if filename.endswith('.txt'):
#         base_name = os.path.splitext(filename)[0]

#         text_path = os.path.join(TEXT_FOLDER, filename)
#         audio_path = os.path.join(AUDIO_FOLDER, base_name + '.mp3')

#         # Find all matching videos starting with base_name
#         matched_videos = sorted([
#             f for f in os.listdir(GIF_FOLDER)
#             if f.startswith(f"{base_name}_") and f.endswith(('.mp4', '.mov', '.avi'))
#         ])

#         if not matched_videos:
#             print(f"No videos found for {base_name}, skipping.")
#             continue

#         print(f"[DEBUG] Matching videos for {base_name}: {matched_videos}")

#         # Resize each video and store paths
#         resized_videos = []
#         for idx, vid_file in enumerate(matched_videos):
#             input_vid = os.path.join(GIF_FOLDER, vid_file)
#             resized_vid = os.path.join(TEMP_FOLDER, f"{base_name}_resized_{idx}.mp4")
#             subprocess.run([
#                 'ffmpeg', '-y', '-i', input_vid,
#                 '-vf', 'scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920',
#                 '-an',
#                 '-c:v', 'libx264',
#                 '-preset', 'veryfast',
#                 '-crf', '23',
#                 resized_vid
#             ], check=True)
#             resized_videos.append(resized_vid)

#         # Create a text file for FFmpeg concat demuxer
#         concat_file = os.path.join(TEMP_FOLDER, f"{base_name}_concat.txt")
#         with open(concat_file, 'w') as f:
#             for rv in resized_videos:
#                 abs_path = os.path.abspath(rv).replace('\\', '/')
#                 f.write(f"file '{abs_path}'\n")

#         # Concatenate videos
#         concatenated_video = os.path.join(TEMP_FOLDER, f"{base_name}_concatenated.mp4")
#         subprocess.run([
#             'ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', concat_file,
#             '-c:v', 'libx264',
#             '-preset', 'veryfast',
#             '-crf', '23',
#             concatenated_video
#         ], check=True)

#         # Load audio duration
#         audio_duration = librosa.get_duration(filename=audio_path)

#         # Trim concatenated video to audio length
#         trimmed_video = os.path.join(TEMP_FOLDER, f"{base_name}_trimmed.mp4")
#         subprocess.run([
#             'ffmpeg', '-y', '-i', concatenated_video,
#             '-t', str(audio_duration),
#             '-c', 'copy',
#             trimmed_video
#         ], check=True)

#         # Pick random background music
#         music_files = [f for f in os.listdir(MUSIC_FOLDER) if f.endswith('.mp3')]
#         music_path = os.path.join(MUSIC_FOLDER, random.choice(music_files)) if music_files else None

#         # Load audio with whisperx
#         audio = whisperx.load_audio(audio_path)

#         # Transcribe audio
#         result = model.transcribe(audio, batch_size=16)

#         # Load alignment model and metadata
#         model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)

#         # Align words with audio
#         aligned = whisperx.align(result["segments"], model_a, metadata, audio, device)
#         word_segments = aligned['word_segments']

#         # Build drawtext filters
#         drawtext_filters = []
#         fontsize = 100
#         fade_in = 0.05
#         fade_out = 0.05

#         for word_data in word_segments:
#             word = word_data['word'].replace("'", "''")
#             start = word_data['start']
#             end = word_data['end']
#             drawtext_filters.append(
#                 f"drawtext=fontfile='{FONT_PATH}':text='{word}':"
#                 f"fontcolor=#FFEA00:fontsize={fontsize}:"
#                 f"shadowcolor=black@0.8:shadowx=2:shadowy=2:"
#                 f"borderw=8:bordercolor=black@0.8:"
#                 f"x=(w-text_w)/2:y=(h*0.65):"
#                 f"enable='between(t,{start - fade_in},{end + fade_out})':"
#                 f"alpha='if(lt(t,{start}),0, if(lt(t,{start}+{fade_in}),(t-{start})/{fade_in}, if(lt(t,{end}),1, if(lt(t,{end}+{fade_out}), 1 - (t - {end})/{fade_out}, 0))))'"
#             )

#         filter_complex = (
#             f"[0:v]{','.join(drawtext_filters)}[v];"
#             f"[1:a]volume=1[a1];"
#         )

#         music_volume = 0.1

#         if music_path:
#             filter_complex += f"[2:a]volume={music_volume}[a2];[a1][a2]amix=inputs=2:duration=first[aout]"
#             inputs = ['-i', trimmed_video, '-i', audio_path, '-i', music_path]
#         else:
#             filter_complex += f"[a1]anull[aout]"
#             inputs = ['-i', trimmed_video, '-i', audio_path]

#         output_path = os.path.join(OUTPUT_FOLDER, base_name + '.mp4')

#         cmd = [
#             'ffmpeg', '-y',
#             *inputs,
#             '-filter_complex', filter_complex,
#             '-map', '[v]',
#             '-map', '[aout]',
#             '-c:v', 'libx264',
#             '-pix_fmt', 'yuv420p',
#             '-c:a', 'aac',
#             '-shortest',
#             output_path
#         ]

#         print(f"\n🎬 Generating: {base_name}.mp4")
#         subprocess.run(cmd, check=True)

#         for filename in os.listdir(TEMP_FOLDER):
#             file_path = os.path.join(TEMP_FOLDER, filename)
#             try:
#                 if os.path.isfile(file_path):
#                     os.remove(file_path)
#                     print(f"file: {filename} removed ✅")
#             except Exception as e:
#                 print(f"Error deleting {filename}: {e}")

# print("\n✅ All videos generated.")




import os
import subprocess
import whisperx

# === Config & paths ===
GIF_FOLDER = './gif'
AUDIO_FILE = './audio/001.mp3'
OUTPUT_FILE = './output_video/final_video.mp4'
TEMP_FOLDER = './temp_resized'
FONT_PATH = './Chewy-Regular.ttf'

os.makedirs(TEMP_FOLDER, exist_ok=True)
os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)

device = "cpu"
compute_type = "int8"

fontsize = 100
fade_in = 0.05
fade_out = 0.05
text_y_position_ratio = 0.85  # <=== Adjustable vertical position of subtitles (0.5 = center, 0.85 = near bottom)

# === Helper: get duration using ffprobe ===
def get_duration(file_path):
    result = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", file_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT
    )
    return float(result.stdout)

# 1. Load audio and get duration
print("🎧 Loading audio and getting duration...")
audio_duration = get_duration(AUDIO_FILE)
print(f"Audio duration: {audio_duration:.2f} seconds")

# 2. Load and transcribe audio with WhisperX
print("🎤 Transcribing audio with WhisperX...")
model = whisperx.load_model("large-v2", device, compute_type=compute_type)
audio_data = whisperx.load_audio(AUDIO_FILE)
result = model.transcribe(audio_data, batch_size=16)
model_a, metadata = whisperx.load_align_model(language_code=result["language"], device=device)
aligned = whisperx.align(result["segments"], model_a, metadata, audio_data, device)
word_segments = aligned['word_segments']

# 3. Get list of videos and compute each segment length
video_files = sorted([os.path.join(GIF_FOLDER, f) for f in os.listdir(GIF_FOLDER) if f.endswith('.mp4')])
num_videos = len(video_files)
if num_videos == 0:
    raise RuntimeError("No videos found in gif folder")

segment_duration = audio_duration / num_videos
print(f"Each video segment duration: {segment_duration:.2f} seconds")

# 4. Process each video: trim + resize
trimmed_videos = []
for i, video in enumerate(video_files):
    trimmed_path = os.path.join(TEMP_FOLDER, f"trimmed_{i}.mp4")

    vf_filter = (
        f"setpts=PTS-STARTPTS,"
        f"scale=1080:1920:force_original_aspect_ratio=increase,"
        f"crop=1080:1920"
    )

    cmd = [
        'ffmpeg', '-y', '-i', video,
        '-t', str(segment_duration),
        '-vf', vf_filter,
        '-an',
        '-c:v', 'libx264',
        '-preset', 'fast',
        trimmed_path
    ]
    subprocess.run(cmd, check=True)
    trimmed_videos.append(trimmed_path)

# Verify trimmed videos exist and durations
print("\nTrimmed videos info:")
for tv in trimmed_videos:
    if not os.path.isfile(tv):
        raise RuntimeError(f"Trimmed video missing: {tv}")
    dur = get_duration(tv)
    print(f"{tv} duration: {dur:.2f} sec")

# 5. Create concat list file with absolute paths and normalized slashes
concat_list_path = os.path.abspath(os.path.join(TEMP_FOLDER, "concat_list.txt")).replace('\\', '/')
with open(concat_list_path, 'w', encoding='utf-8') as f:
    for tv in trimmed_videos:
        abs_path = os.path.abspath(tv).replace('\\', '/')
        f.write(f"file '{abs_path}'\n")

# Print concat_list.txt content for debug
print("\nContents of concat_list.txt:")
with open(concat_list_path, 'r', encoding='utf-8') as f:
    print(f.read())

concatenated_video_path = os.path.abspath(os.path.join(TEMP_FOLDER, "concatenated.mp4")).replace('\\', '/')

# 6. Concatenate trimmed videos (re-encode)
cmd_concat = [
    'ffmpeg', '-y',
    '-f', 'concat',
    '-safe', '0',
    '-i', concat_list_path,
    '-c:v', 'libx264',
    '-preset', 'fast',
    '-pix_fmt', 'yuv420p',
    '-an',
    concatenated_video_path
]

print("📦 Concatenating trimmed videos into one sequential video with re-encoding...")
subprocess.run(cmd_concat, check=True)

# 7. Generate subtitle drawtext filters
drawtext_filters = []
for ws in word_segments:
    start, end, word = ws['start'], ws['end'], ws['word'].replace("'", "''")
    drawtext_filters.append(
        f"drawtext=fontfile='{FONT_PATH}':text='{word}':"
        f"fontcolor=#FFEA00:fontsize={fontsize}:"
        f"shadowcolor=black@0.8:shadowx=2:shadowy=2:"
        f"borderw=8:bordercolor=black@0.8:"
        f"x=(w-text_w)/2:y=(h*{text_y_position_ratio}):"
        f"enable='between(t,{start - fade_in},{end + fade_out})':"
        f"alpha='if(lt(t,{start}),0,"
        f"if(lt(t,{start}+{fade_in}),(t-{start})/{fade_in},"
        f"if(lt(t,{end}),1,"
        f"if(lt(t,{end}+{fade_out}),1-(t-{end})/{fade_out},0))))'"
    )
drawtext_filter_str = ",".join(drawtext_filters)

# 8. Generate final video with subtitles + audio
final_cmd = [
    'ffmpeg', '-y',
    '-i', concatenated_video_path,
    '-i', AUDIO_FILE,
    '-filter_complex', f"[0:v]{drawtext_filter_str}[v]",
    '-map', '[v]', '-map', '1:a',
    '-c:v', 'libx264', '-preset', 'fast',
    '-c:a', 'aac', '-b:a', '192k',
    '-pix_fmt', 'yuv420p',
    '-shortest',
    OUTPUT_FILE
]

print("🎬 Generating final video with subtitles and audio...")
subprocess.run(final_cmd, check=True)

# 9. Clean up temp folder
for filename in os.listdir(TEMP_FOLDER):
    file_path = os.path.join(TEMP_FOLDER, filename)
    try:
        if os.path.isfile(file_path):
            os.remove(file_path)
            print(f"file: {filename} removed ✅")
    except Exception as e:
        print(f"Error deleting {filename}: {e}")

print(f"✅ Final video created: {OUTPUT_FILE}")
