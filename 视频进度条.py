import json
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont
from tqdm import tqdm

def load_config(filename):
    with open(filename, 'r', encoding='utf-8') as config_file:
        config = json.load(config_file)
    return config

def export_frame(frame_number, total_frames, is_reversed, img_width, img_height, bar_width, filled_dimension, background_color, progress_color, is_horizontal, chapters, chapter_titles, chapter_separator_color, title_font, title_font_size, title_font_color, video_duration):
    # 参数：
    # output_file (str): 输出文件名
    # video_duration (int): 视频时长（秒）
    # progress_color (tuple): 进度条颜色 (B, G, R)
    # background_color (tuple): 进度条底色 (B, G, R)
    # bar_dimension (int): 进度条长度或高度
    # bar_width (int, 可选): 进度条宽度或高度，默认值为None，表示使用默认值
    # chapters (list, 可选): 章节分隔时间点列表，默认值为None，表示没有章节
    # chapter_titles (list, 可选): 章节标题列表，默认值为None，表示没有章节标题
    # chapter_separator_color (tuple, 可选): 章节分隔符颜色 (B, G, R)，默认为白色
    # is_horizontal (bool): 是否横向进度条
    # is_reversed (bool): 是否反向
    # title_font (str, 可选): 标题文本字体文件路径，默认值为None，表示使用默认字体
    # title_font_size (int, 可选): 标题文本字体大小，默认值为20
    # title_font_color (tuple, 可选): 标题文本颜色 (B, G, R)，默认为白色

    # 返回：
    # 无

    progress = frame_number / total_frames
    if is_reversed:
        progress = 1 - progress
    filled_length = int(progress * filled_dimension)

    image = np.zeros((img_height, img_width, 3), dtype=np.uint8)
    image[:, :] = background_color

    if is_horizontal:
        image[:bar_width, :filled_length, :] = progress_color
    else:
        image[:filled_length, :bar_width, :] = progress_color

    if chapters and chapter_titles:
        prev_separator_position = 0

        for i in range(len(chapters)):
            chapter_time = chapters[i]
            chapter_title = chapter_titles[i]

            chapter_progress = chapter_time / video_duration

            if is_reversed:
                chapter_progress = 1 - chapter_progress

            separator_position = int(chapter_progress * filled_dimension)

            if is_horizontal:
                font = ImageFont.truetype(title_font, title_font_size)
                text = chapter_title
                text_size = font.getbbox(text)

                text_x = prev_separator_position + \
                    (separator_position -
                     prev_separator_position - text_size[2]) // 2
                text_y = bar_width // 2 - text_size[3] // 2

                pil_image = Image.fromarray(image)
                draw = ImageDraw.Draw(pil_image)
                draw.text((text_x, text_y), text,
                          title_font_color, font=font)
                image = np.array(pil_image)

                image[:bar_width, separator_position,
                      :] = chapter_separator_color
                prev_separator_position = separator_position

            else:
                font = ImageFont.truetype(title_font, title_font_size)
                text = chapter_title
                text_size = font.getbbox(text)

                text_x = bar_width // 2 - text_size[2] // 2
                text_y = prev_separator_position + \
                    (separator_position - prev_separator_position) // 2 - text_size[3] // 2  # 修改这一行

                pil_image = Image.fromarray(image)
                draw = ImageDraw.Draw(pil_image)
                draw.text((text_x, text_y), text,
                          title_font_color, font=font)
                image = np.array(pil_image)

                image[separator_position, :bar_width,
                      :] = chapter_separator_color
                prev_separator_position = separator_position

        if is_horizontal:
            font = ImageFont.truetype(title_font, title_font_size)
            text = chapter_titles[-1]
            text_size = font.getbbox(text)

            text_x = prev_separator_position + \
                (filled_dimension -
                 prev_separator_position - text_size[2]) // 2
            text_y = bar_width // 2 - text_size[3] // 2

            pil_image = Image.fromarray(image)
            draw = ImageDraw.Draw(pil_image)
            draw.text((text_x, text_y), text, title_font_color, font=font)
            image = np.array(pil_image)

        else:
            font = ImageFont.truetype(title_font, title_font_size)
            text = chapter_titles[-1]
            text_size = font.getbbox(text)

            text_x = bar_width // 2 - text_size[2] // 2
            text_y = prev_separator_position + \
                (filled_dimension -
                 prev_separator_position) // 2 - text_size[3] // 2  # 修改这一行

            pil_image = Image.fromarray(image)
            draw = ImageDraw.Draw(pil_image)
            draw.text((text_x, text_y), text, title_font_color, font=font)
            image = np.array(pil_image)

    return image

def create_progress_bar_video_sequence(config_file):
    config = load_config(config_file)

    output_file = config["output_file"]
    video_duration = config["video_duration"]
    progress_color = tuple(config["progress_color"])
    background_color = tuple(config["background_color"])
    bar_dimension = config["bar_dimension"]
    bar_width = config.get("bar_width", None)
    chapters = config["chapters"]
    chapter_titles = config["chapter_titles"]
    chapter_separator_color = tuple(config["chapter_separator_color"])
    is_horizontal = config["is_horizontal"]
    is_reversed = config["is_reversed"]
    title_font = config["title_font"]
    title_font_size = config["title_font_size"]
    title_font_color = tuple(config["title_font_color"])

    if bar_width is None:
        bar_width = 40

    if is_horizontal:
        img_width = bar_dimension
        img_height = bar_width
        filled_dimension = img_width
    else:
        img_width = bar_width
        img_height = bar_dimension
        filled_dimension = img_height

    fourcc = cv2.VideoWriter_fourcc(*'MJPG')
    out = cv2.VideoWriter(output_file, fourcc, 30, (img_width, img_height))

    total_frames = int(video_duration * 30)

    for frame_number in tqdm(range(total_frames), desc="Exporting Frames", ncols=100):
        frame = export_frame(frame_number, total_frames, is_reversed, img_width, img_height, bar_width, filled_dimension, background_color, progress_color, is_horizontal, chapters, chapter_titles, chapter_separator_color, title_font, title_font_size, title_font_color, video_duration)
        out.write(frame)

    out.release()

if __name__ == "__main__":
    create_progress_bar_video_sequence('黑红白横.json')