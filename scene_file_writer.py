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
    """打开一个视频管道，用于通过ffmpeg写入视频帧数据"""
    # 分离文件路径的文件名和扩展名
    stem, ext = os.path.splitext(file_path)
    self.final_file_path = file_path  # 最终视频文件路径
    self.temp_file_path = stem + "_temp" + ext  # 临时视频文件路径（用于中间处理）

    # 获取场景相机的帧率和像素尺寸
    fps = self.scene.camera.fps
    width, height = self.scene.camera.get_pixel_shape()

    # 构建ffmpeg的视频滤镜参数：垂直翻转并调整饱和度和伽马值
    vf_arg = 'vflip'  # 垂直翻转（因为渲染输出可能是上下颠倒的）
    vf_arg += f',eq=saturation={self.saturation}:gamma={self.gamma}'  # 调整饱和度和伽马

    # 构建ffmpeg命令
    command = [
        self.ffmpeg_bin,  # ffmpeg可执行文件
        '-y',  # 如果输出文件存在则覆盖
        '-f', 'rawvideo',  # 输入格式为原始视频数据
        '-s', f'{width}x{height}',  # 视频帧尺寸
        '-pix_fmt', 'rgba',  # 像素格式为RGBA
        '-r', str(fps),  # 帧率
        '-i', '-',  # 输入来自管道
        '-vf', vf_arg,  # 应用视频滤镜
        '-an',  # 不处理音频（此时还未添加音频）
        '-loglevel', 'error',  # 只输出错误日志
    ]
    # 如果指定了视频编码器，添加到命令中
    if self.video_codec:
        command += ['-vcodec', self.video_codec]
    # 如果指定了像素格式，添加到命令中
    if self.pixel_format:
        command += ['-pix_fmt', self.pixel_format]
    # 添加输出文件路径（临时文件）
    command += [self.temp_file_path]
    # 启动ffmpeg进程，通过管道输入数据
    self.writing_process = sp.Popen(command, stdin=sp.PIPE)

    # 如果不是静默模式，初始化进度条
    if not self.quiet:
        self.progress_display = ProgressDisplay(
            range(self.total_frames),  # 总帧数范围
            leave=False,  # 进度条完成后不保留
            ascii=True if platform.system() == 'Windows' else None,  # Windows系统使用ASCII字符显示进度条
            dynamic_ncols=True,  # 动态调整进度条宽度
        )
        self.set_progress_display_description()  # 设置进度条描述

def use_fast_encoding(self):
    """使用快速编码模式（牺牲部分质量换取速度）"""
    self.video_codec = "libx264rgb"  # 使用RGB编码器，避免颜色空间转换
    self.pixel_format = "rgb32"  # 使用RGB32像素格式

def get_insert_file_path(self, index: int) -> Path:
    """获取插入片段的文件路径"""
    movie_path = Path(self.get_movie_file_path())
    scene_name = movie_path.stem  # 获取场景名称（不含扩展名）
    insert_dir = Path(movie_path.parent, "inserts")  # 插入片段存放目录
    guarantee_existence(insert_dir)  # 确保目录存在
    # 返回带索引的插入片段路径
    return Path(insert_dir, f"{scene_name}_{index}").with_suffix(self.movie_file_extension)

def begin_insert(self):
    """开始写入一个插入片段"""
    # 临时开启视频写入功能
    self.write_to_movie = True
    self.init_output_directories()  # 初始化输出目录
    index = 0
    # 找到第一个不存在的插入片段路径（避免覆盖）
    while (insert_path := self.get_insert_file_path(index)).exists():
        index += 1
    self.inserted_file_path = insert_path  # 记录插入片段路径
    self.open_movie_pipe(self.inserted_file_path)  # 打开视频管道

def end_insert(self):
    """结束插入片段的写入"""
    self.close_movie_pipe()  # 关闭视频管道
    self.write_to_movie = False  # 恢复原有的视频写入设置
    self.print_file_ready_message(self.inserted_file_path)  # 打印插入片段就绪消息

def has_progress_display(self):
    """检查是否有进度条显示"""
    return self.progress_display is not None

def set_progress_display_description(self, file: str = "", sub_desc: str = "") -> None:
    """设置进度条的描述文本"""
    if self.progress_display is None:
        return  # 没有进度条则直接返回

    desc_len = self.progress_description_len  # 描述文本的长度限制
    if not file:
        # 如果未指定文件，使用当前视频文件的名称
        file = os.path.split(self.get_movie_file_path())[1]
    full_desc = f"{file} {sub_desc}"  # 完整描述文本
    # 如果描述文本过长，进行截断并添加省略号
    if len(full_desc) > desc_len:
        full_desc = full_desc[:desc_len - 3] + "..."
    else:
        # 如果过短，用空格填充到指定长度
        full_desc += " " * (desc_len - len(full_desc))
    # 设置进度条描述
    self.progress_display.set_description(full_desc)

def write_frame(self, camera: Camera) -> None:
    """将当前相机捕获的帧写入视频管道"""
    if self.write_to_movie:
        # 获取原始帧数据（字节形式）
        raw_bytes = camera.get_raw_fbo_data()
        # 将帧数据写入ffmpeg进程的标准输入
        self.writing_process.stdin.write(raw_bytes)
        # 如果有进度条，更新进度
        if self.progress_display is not None:
            self.progress_display.update()

def close_movie_pipe(self) -> None:
    """关闭视频管道，完成视频文件的写入"""
    # 关闭标准输入，告诉ffmpeg没有更多数据
    self.writing_process.stdin.close()
    # 等待ffmpeg进程完成
    self.writing_process.wait()
    # 终止ffmpeg进程
    self.writing_process.terminate()
    # 关闭进度条
    if self.progress_display is not None:
        self.progress_display.close()

    # 如果不是因为中断结束，将临时文件移动到最终路径
    if not self.ended_with_interrupt:
        shutil.move(self.temp_file_path, self.final_file_path)
    else:
        # 如果是中断结束，保留临时文件
        self.movie_file_path = self.temp_file_path

def add_sound_to_video(self) -> None:
    """将音频添加到视频文件中"""
    movie_file_path = self.get_movie_file_path()
    # 分离文件名和扩展名
    stem, ext = os.path.splitext(movie_file_path)
    sound_file_path = stem + ".wav"  # 临时音频文件路径

    # 添加一个0长度的静音片段，确保音频长度与视频匹配
    self.add_audio_segment(AudioSegment.silent(0))
    # 导出音频片段到WAV文件
    self.audio_segment.export(
        sound_file_path,
        bitrate='312k',  # 音频比特率
    )

    # 临时文件路径（用于合并音频和视频）
    temp_file_path = stem + "_temp" + ext
    # 构建合并音频和视频的ffmpeg命令
    commands = [
        self.ffmpeg_bin,
        "-i", movie_file_path,  # 输入视频文件
        "-i", sound_file_path,  # 输入音频文件
        '-y',  # 覆盖输出文件
        "-c:v", "copy",  # 视频流直接复制（不重新编码）
        "-c:a", "aac",  # 音频编码为AAC
        "-b:a", "320k",  # 音频比特率
        # 选择第一个文件的视频流
        "-map", "0:v:0",
        # 选择第二个文件的音频流
        "-map", "1:a:0",
        '-loglevel', 'error',  # 只输出错误日志
        temp_file_path,  # 输出临时文件
    ]
    # 执行ffmpeg命令
    sp.call(commands)
    # 将临时文件移动到最终路径
    shutil.move(temp_file_path, movie_file_path)
    # 删除临时音频文件
    os.remove(sound_file_path)

def save_final_image(self, image: Image) -> None:
    """保存最终帧为图像文件"""
    file_path = self.get_image_file_path()
    image.save(file_path)  # 保存图像
    self.print_file_ready_message(file_path)  # 打印图像就绪消息

def print_file_ready_message(self, file_path: str) -> None:
    """打印文件就绪的消息"""
    if not self.quiet:
        log.info(f"File ready at {file_path}")  # 输出文件路径信息

def should_open_file(self) -> bool:
    """判断是否应该打开文件或显示文件位置"""
    return any([
        self.show_file_location_upon_completion,  # 显示文件位置
        self.open_file_upon_completion,  # 打开文件
    ])

def open_file(self) -> None:
    """打开生成的文件或显示其位置"""
    if self.quiet:
        # 静默模式下，临时重定向标准输出到空设备
        curr_stdout = sys.stdout
        sys.stdout = open(os.devnull, "w")

    current_os = platform.system()  # 获取当前操作系统
    file_paths = []  # 要处理的文件路径列表

    # 收集需要打开的文件路径
    if self.save_last_frame:
        file_paths.append(self.get_image_file_path())
    if self.write_to_movie:
        file_paths.append(self.get_movie_file_path())

    # 逐个处理文件
    for file_path in file_paths:
        if current_os == "Windows":
            # Windows系统使用startfile打开文件
            os.startfile(file_path)
        else:
            commands = []
            # 根据操作系统选择合适的命令
            if current_os == "Linux":
                commands.append("xdg-open")  # Linux使用xdg-open
            elif current_os.startswith("CYGWIN"):
                commands.append("cygstart")  # Cygwin使用cygstart
            else:  # 默认为macOS
                commands.append("open")  # macOS使用open

            # 如果需要显示文件位置而非打开文件
            if self.show_file_location_upon_completion:
                commands.append("-R")  # macOS的-R参数显示文件在Finder中的位置

            commands.append(file_path)  # 添加文件路径

            # 执行命令，重定向输出到空设备
            FNULL = open(os.devnull, 'w')
            sp.call(commands, stdout=FNULL, stderr=sp.STDOUT)
            FNULL.close()

    if self.quiet:
        # 恢复标准输出
        sys.stdout.close()
        sys.stdout = curr_stdout