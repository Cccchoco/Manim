from __future__ import annotations

import os
import platform
import shutil
import subprocess as sp  # 用于执行外部命令（如ffmpeg）
import sys

import numpy as np  # 用于数值计算
from pydub import AudioSegment  # 用于音频处理
from tqdm.auto import tqdm as ProgressDisplay  # 用于显示进度条
from pathlib import Path  # 用于路径处理

from manimlib.logger import log  # manim的日志工具
from manimlib.mobject.mobject import Mobject  # manim的基本图形对象类
from manimlib.utils.file_ops import guarantee_existence  # 确保目录存在的工具函数
from manimlib.utils.sounds import get_full_sound_file_path  # 获取完整声音文件路径的工具函数

from typing import TYPE_CHECKING  # 用于类型提示的条件导入

# 类型检查时导入所需的类，避免循环导入问题
if TYPE_CHECKING:
    from PIL.Image import Image  # 图像类型

    from manimlib.camera.camera import Camera  # 相机类
    from manimlib.scene.scene import Scene  # 场景类


class SceneFileWriter(object):
    """场景文件写入器，负责将场景渲染为视频或图像文件"""
    
    def __init__(
        self,
        scene: Scene,
        write_to_movie: bool = False,  # 是否写入视频文件
        subdivide_output: bool = False,  # 是否将输出分割为多个部分
        png_mode: str = "RGBA",  # 保存PNG图像的模式
        save_last_frame: bool = False,  # 是否保存最后一帧
        movie_file_extension: str = ".mp4",  # 视频文件扩展名
        # 输出位置相关参数
        output_directory: str = ".",  # 输出目录
        file_name: str | None = None,  # 文件名
        open_file_upon_completion: bool = False,  # 完成后是否打开文件
        show_file_location_upon_completion: bool = False,  # 完成后是否显示文件位置
        quiet: bool = False,  # 是否静默模式（不显示进度）
        total_frames: int = 0,  # 总帧数
        progress_description_len: int = 40,  # 进度描述的长度
        # ffmpeg相关参数
        ffmpeg_bin: str = "ffmpeg",  # ffmpeg可执行文件名称
        video_codec: str = "libx264",  # 视频编码器
        pixel_format: str = "yuv420p",  # 像素格式
        saturation: float = 1.0,  # 饱和度
        gamma: float = 1.0,  # 伽马值
    ):
        self.scene: Scene = scene  # 关联的场景对象
        self.write_to_movie = write_to_movie  # 是否写入视频
        self.subdivide_output = subdivide_output  # 是否分割输出
        self.png_mode = png_mode  # PNG图像模式
        self.save_last_frame = save_last_frame  # 是否保存最后一帧
        self.movie_file_extension = movie_file_extension  # 视频扩展名
        self.output_directory = output_directory  # 输出目录
        self.file_name = file_name  # 文件名
        self.open_file_upon_completion = open_file_upon_completion  # 完成后打开文件
        self.show_file_location_upon_completion = show_file_location_upon_completion  # 显示文件位置
        self.quiet = quiet  # 静默模式
        self.total_frames = total_frames  # 总帧数
        self.progress_description_len = progress_description_len  # 进度描述长度
        self.ffmpeg_bin = ffmpeg_bin  # ffmpeg二进制文件
        self.video_codec = video_codec  # 视频编码器
        self.pixel_format = pixel_format  # 像素格式
        self.saturation = saturation  # 饱和度
        self.gamma = gamma  # 伽马值

        # 文件写入过程中的状态变量
        self.writing_process: sp.Popen | None = None  # 写入进程（ffmpeg）
        self.progress_display: ProgressDisplay | None = None  # 进度条显示
        self.ended_with_interrupt: bool = False  # 是否因中断结束

        # 初始化输出目录和音频
        self.init_output_directories()
        self.init_audio()

    # 输出目录和文件相关方法
    def init_output_directories(self) -> None:
        """初始化所有必要的输出目录"""
        if self.save_last_frame:
            self.image_file_path = self.init_image_file_path()
        if self.write_to_movie:
            self.movie_file_path = self.init_movie_file_path()
        if self.subdivide_output:
            self.partial_movie_directory = self.init_partial_movie_directory()

    def init_image_file_path(self) -> Path:
        """初始化图像文件路径"""
        return self.get_output_file_rootname().with_suffix(".png")

    def init_movie_file_path(self) -> Path:
        """初始化视频文件路径"""
        return self.get_output_file_rootname().with_suffix(self.movie_file_extension)

    def init_partial_movie_directory(self):
        """初始化部分视频文件的存放目录"""
        return guarantee_existence(self.get_output_file_rootname())

    def get_output_file_rootname(self) -> Path:
        """获取输出文件的根路径（不含扩展名）"""
        return Path(
            guarantee_existence(self.output_directory),  # 确保输出目录存在
            self.get_output_file_name()  # 获取输出文件名
        )

    def get_output_file_name(self) -> str:
        """获取输出文件名（不含路径和扩展名）"""
        if self.file_name:
            return self.file_name
        # 否则，使用场景名称，可能附加动画编号
        name = str(self.scene)
        saan = self.scene.start_at_animation_number  # 开始动画编号
        eaan = self.scene.end_at_animation_number  # 结束动画编号
        if saan is not None:
            name += f"_{saan}"
        if eaan is not None:
            name += f"_{eaan}"
        return name

    # 目录获取方法
    def get_image_file_path(self) -> str:
        """获取图像文件路径"""
        return self.image_file_path

    def get_next_partial_movie_path(self) -> str:
        """获取下一个部分视频文件的路径"""
        result = Path(self.partial_movie_directory, f"{self.scene.num_plays:05}")
        return result.with_suffix(self.movie_file_extension)

    def get_movie_file_path(self) -> str:
        """获取完整视频文件的路径"""
        return self.movie_file_path

    # 音频相关方法
    def init_audio(self) -> None:
        """初始化音频相关变量"""
        self.includes_sound: bool = False  # 是否包含声音

    def create_audio_segment(self) -> None:
        """创建一个空的音频片段"""
        self.audio_segment = AudioSegment.silent()

    def add_audio_segment(
        self,
        new_segment: AudioSegment,  # 要添加的音频片段
        time: float | None = None,  # 插入时间点（秒）
        gain_to_background: float | None = None  # 叠加时的背景增益
    ) -> None:
        """添加音频片段到音频轨道"""
        if not self.includes_sound:
            self.includes_sound = True
            self.create_audio_segment()
        segment = self.audio_segment
        curr_end = segment.duration_seconds  # 当前音频的结束时间
        if time is None:
            time = curr_end  # 默认添加到末尾
        if time < 0:
            raise Exception("Adding sound at timestamp < 0")  # 不允许负时间点

        new_end = time + new_segment.duration_seconds  # 新的结束时间
        diff = new_end - curr_end  # 计算需要补充的静音时长
        if diff > 0:
            # 补充静音以确保新片段能正确插入
            segment = segment.append(
                AudioSegment.silent(int(np.ceil(diff * 1000))),  # 毫秒为单位
                crossfade=0,  # 无交叉淡入淡出
            )
        # 将新片段叠加到主音频轨道
        self.audio_segment = segment.overlay(
            new_segment,
            position=int(1000 * time),  # 位置（毫秒）
            gain_during_overlay=gain_to_background,  # 叠加时的增益
        )

    def add_sound(
        self,
        sound_file: str,  # 声音文件路径
        time: float | None = None,  # 插入时间点
        gain: float | None = None,  # 声音增益
        gain_to_background: float | None = None  # 叠加时的背景增益
    ) -> None:
        """添加声音文件到音频轨道"""
        file_path = get_full_sound_file_path(sound_file)  # 获取完整路径
        new_segment = AudioSegment.from_file(file_path)  # 加载音频文件
        if gain:
            new_segment = new_segment.apply_gain(gain)  # 应用增益
        # 添加到音频轨道
        self.add_audio_segment(new_segment, time, gain_to_background)

    # 写入器控制方法
    def begin(self) -> None:
        """开始写入过程"""
        if not self.subdivide_output and self.write_to_movie:
            # 非分割模式下，直接打开视频管道
            self.open_movie_pipe(self.get_movie_file_path())

    def begin_animation(self) -> None:
        """开始一个动画片段的写入"""
        if self.subdivide_output and self.write_to_movie:
            # 分割模式下，为每个动画片段打开单独的视频管道
            self.open_movie_pipe(self.get_next_partial_movie_path())

    def end_animation(self) -> None:
        """结束当前动画片段的写入"""
        if self.subdivide_output and self.write_to_movie:
            # 关闭当前视频管道
            self.close_movie_pipe()

    def finish(self) -> None:
        """完成所有写入操作"""
        if not self.subdivide_output and self.write_to_movie:
            # 关闭视频管道
            self.close_movie_pipe()
            # 如果包含声音，将音频添加到视频
            if self.includes_sound:
                self.add_sound_to_video()
            # 打印文件就绪消息
            self.print_file_ready_message(self.get_movie_file_path())
        # 如果需要保存最后一帧
        if self.save_last_frame:
            self.scene.update_frame(force_draw=True)  # 强制更新帧
            self.save_final_image(self.scene.get_image())  # 保存图像
        # 如果需要打开文件
        if self.should_open_file():
            self.open_file()

    def open_movie_pipe(self, file_path: str) -> None:
        stem, ext = os.path.splitext(file_path)
        self.final_file_path = file_path
        self.temp_file_path = stem + "_temp" + ext

        fps = self.scene.camera.fps
        width, height = self.scene.camera.get_pixel_shape()

        vf_arg = 'vflip'
        vf_arg += f',eq=saturation={self.saturation}:gamma={self.gamma}'

        command = [
            self.ffmpeg_bin,
            '-y',  # overwrite output file if it exists
            '-f', 'rawvideo',
            '-s', f'{width}x{height}',  # size of one frame
            '-pix_fmt', 'rgba',
            '-r', str(fps),  # frames per second
            '-i', '-',  # The input comes from a pipe
            '-vf', vf_arg,
            '-an',  # Tells ffmpeg not to expect any audio
            '-loglevel', 'error',
        ]
        if self.video_codec:
            command += ['-vcodec', self.video_codec]
        if self.pixel_format:
            command += ['-pix_fmt', self.pixel_format]
        command += [self.temp_file_path]
        self.writing_process = sp.Popen(command, stdin=sp.PIPE)

        if not self.quiet:
            self.progress_display = ProgressDisplay(
                range(self.total_frames),
                leave=False,
                ascii=True if platform.system() == 'Windows' else None,
                dynamic_ncols=True,
            )
            self.set_progress_display_description()

    def use_fast_encoding(self):
        self.video_codec = "libx264rgb"
        self.pixel_format = "rgb32"

    def get_insert_file_path(self, index: int) -> Path:
        movie_path = Path(self.get_movie_file_path())
        scene_name = movie_path.stem
        insert_dir = Path(movie_path.parent, "inserts")
        guarantee_existence(insert_dir)
        return Path(insert_dir, f"{scene_name}_{index}").with_suffix(self.movie_file_extension)

    def begin_insert(self):
        # Begin writing process
        self.write_to_movie = True
        self.init_output_directories()
        index = 0
        while (insert_path := self.get_insert_file_path(index)).exists():
            index += 1
        self.inserted_file_path = insert_path
        self.open_movie_pipe(self.inserted_file_path)

    def end_insert(self):
        self.close_movie_pipe()
        self.write_to_movie = False
        self.print_file_ready_message(self.inserted_file_path)

    def has_progress_display(self):
        return self.progress_display is not None

    def set_progress_display_description(self, file: str = "", sub_desc: str = "") -> None:
        if self.progress_display is None:
            return

        desc_len = self.progress_description_len
        if not file:
            file = os.path.split(self.get_movie_file_path())[1]
        full_desc = f"{file} {sub_desc}"
        if len(full_desc) > desc_len:
            full_desc = full_desc[:desc_len - 3] + "..."
        else:
            full_desc += " " * (desc_len - len(full_desc))
        self.progress_display.set_description(full_desc)

    def write_frame(self, camera: Camera) -> None:
        if self.write_to_movie:
            raw_bytes = camera.get_raw_fbo_data()
            self.writing_process.stdin.write(raw_bytes)
            if self.progress_display is not None:
                self.progress_display.update()

    def close_movie_pipe(self) -> None:
        self.writing_process.stdin.close()
        self.writing_process.wait()
        self.writing_process.terminate()
        if self.progress_display is not None:
            self.progress_display.close()

        if not self.ended_with_interrupt:
            shutil.move(self.temp_file_path, self.final_file_path)
        else:
            self.movie_file_path = self.temp_file_path

    def add_sound_to_video(self) -> None:
        movie_file_path = self.get_movie_file_path()
        stem, ext = os.path.splitext(movie_file_path)
        sound_file_path = stem + ".wav"
        # Makes sure sound file length will match video file
        self.add_audio_segment(AudioSegment.silent(0))
        self.audio_segment.export(
            sound_file_path,
            bitrate='312k',
        )
        temp_file_path = stem + "_temp" + ext
        commands = [
            self.ffmpeg_bin,
            "-i", movie_file_path,
            "-i", sound_file_path,
            '-y',  # overwrite output file if it exists
            "-c:v", "copy",
            "-c:a", "aac",
            "-b:a", "320k",
            # select video stream from first file
            "-map", "0:v:0",
            # select audio stream from second file
            "-map", "1:a:0",
            '-loglevel', 'error',
            # "-shortest",
            temp_file_path,
        ]
        sp.call(commands)
        shutil.move(temp_file_path, movie_file_path)
        os.remove(sound_file_path)

    def save_final_image(self, image: Image) -> None:
        file_path = self.get_image_file_path()
        image.save(file_path)
        self.print_file_ready_message(file_path)

    def print_file_ready_message(self, file_path: str) -> None:
        if not self.quiet:
            log.info(f"File ready at {file_path}")

    def should_open_file(self) -> bool:
        return any([
            self.show_file_location_upon_completion,
            self.open_file_upon_completion,
        ])

    def open_file(self) -> None:
        if self.quiet:
            curr_stdout = sys.stdout
            sys.stdout = open(os.devnull, "w")

        current_os = platform.system()
        file_paths = []

        if self.save_last_frame:
            file_paths.append(self.get_image_file_path())
        if self.write_to_movie:
            file_paths.append(self.get_movie_file_path())

        for file_path in file_paths:
            if current_os == "Windows":
                os.startfile(file_path)
            else:
                commands = []
                if current_os == "Linux":
                    commands.append("xdg-open")
                elif current_os.startswith("CYGWIN"):
                    commands.append("cygstart")
                else:  # Assume macOS
                    commands.append("open")

                if self.show_file_location_upon_completion:
                    commands.append("-R")

                commands.append(file_path)

                FNULL = open(os.devnull, 'w')
                sp.call(commands, stdout=FNULL, stderr=sp.STDOUT)
                FNULL.close()

        if self.quiet:
            sys.stdout.close()
            sys.stdout = curr_stdout
