# 从__future__导入annotations，支持在类型注解中使用尚未定义的类
from __future__ import annotations

# 从abc模块导入抽象基类相关工具，用于定义必须被重写的方法
from abc import ABC, abstractmethod

# 导入numpy库，用于数值计算
import numpy as np

# 从动画模块导入Animation基类，所有具体动画类都继承自它
from manimlib.animation.animation import Animation

# 导入字符串相关的可动对象类，用于处理文本字符串的动画
from manimlib.mobject.svg.string_mobject import StringMobject

# 导入矢量可动对象基类，用于处理矢量图形的动画
from manimlib.mobject.types.vectorized_mobject import VMobject

# 导入贝塞尔曲线相关的整数插值函数
from manimlib.utils.bezier import integer_interpolate

# 导入各种速率函数，用于控制动画的速度变化曲线
from manimlib.utils.rate_functions import linear  # 线性速率函数
from manimlib.utils.rate_functions import double_smooth  # 双平滑速率函数（开始和结束都平滑）
from manimlib.utils.rate_functions import smooth  # 平滑速率函数（常用的缓动函数）

# 导入截断函数，用于将值限制在特定范围内
from manimlib.utils.simple_functions import clip

# 导入类型检查相关模块
from typing import TYPE_CHECKING

# 当进行类型检查时（运行时不会执行），导入所需的类型提示
if TYPE_CHECKING:
    from typing import Callable
    from manimlib.mobject.mobject import Mobject
    from manimlib.scene.scene import Scene
    from manimlib.typing import ManimColor


class ShowPartial(Animation, ABC):
    """
    抽象类，作为ShowCreation和ShowPassingFlash的基类
    用于实现物体部分显示的动画效果
    """
    def __init__(self, mobject: Mobject, should_match_start: bool = False, **kwargs):
        # 标记是否应该匹配起始状态
        self.should_match_start = should_match_start
        # 调用父类Animation的初始化方法，传递mobject和其他关键字参数
        super().__init__(mobject,** kwargs)

    def interpolate_submobject(
        self,
        submob: VMobject,
        start_submob: VMobject,
        alpha: float
    ) -> None:
        """
        插值处理子物体，定义动画过程中每个子物体的状态变化
        
        参数:
            submob: 要进行插值的子物体
            start_submob: 子物体的起始状态
            alpha: 动画进度，范围从0到1
        """
        # 使子物体部分地变成起始状态的一部分
        # 具体显示哪部分由get_bounds(alpha)返回的边界决定
        submob.pointwise_become_partial(
            start_submob, *self.get_bounds(alpha)
        )

   # 定义抽象方法 get_bounds，要求子类必须实现该方法
# 参数 alpha 为浮点型，返回值为包含两个浮点数的元组
@abstractmethod
def get_bounds(self, alpha: float) -> tuple[float, float]:
    # 如果子类未实现该方法，则抛出异常提示
    raise Exception("Not Implemented")


# 定义 ShowCreation 类，继承自 ShowPartial 类
class ShowCreation(ShowPartial):
    # 构造方法，初始化 ShowCreation 实例
    # 参数：
    #   mobject: 要展示的动画对象
    #   lag_ratio: 延迟比例，默认为 1.0
    #   **kwargs: 其他关键字参数，传递给父类构造方法
    def __init__(self, mobject: Mobject, lag_ratio: float = 1.0,** kwargs):
        # 调用父类 ShowPartial 的构造方法，传递参数
        super().__init__(mobject, lag_ratio=lag_ratio, **kwargs)

    # 实现父类的抽象方法 get_bounds
    # 返回当前动画进度对应的边界范围 (0, alpha)
    # alpha 表示动画进度（0 为开始，1 为结束）
    def get_bounds(self, alpha: float) -> tuple[float, float]:
        return (0, alpha)


# 定义 Uncreate 类，继承自 ShowCreation 类
class Uncreate(ShowCreation):
    # 构造方法，初始化 Uncreate 实例
    # 参数：
    #   mobject: 要展示的动画对象
    #   rate_func: 速率函数，控制动画速度变化，默认为反向平滑函数
    #   remover: 是否在动画结束后移除对象，默认为 True
    #   should_match_start: 是否匹配起始状态，默认为 True
    #   **kwargs: 其他关键字参数，传递给父类构造方法
    def __init__(
        self,
        mobject: Mobject,
        rate_func: Callable[[float], float] = lambda t: smooth(1 - t),
        remover: bool = True,
        should_match_start: bool = True,** kwargs,
    ):
        # 调用父类 ShowCreation 的构造方法，传递参数
        super().__init__(
            mobject,
            rate_func=rate_func,
            remover=remover,
            should_match_start=should_match_start,
            **kwargs,
        )


class DrawBorderThenFill(Animation):
    """
    一个自定义动画类，先绘制VMobject的边框，然后填充内部颜色
    继承自Manim的Animation基类，实现了先描边后填充的动画效果
    """
    def __init__(
        self,
        vmobject: VMobject,
        run_time: float = 2.0,
        rate_func: Callable[[float], float] = double_smooth,
        stroke_width: float = 2.0,
        stroke_color: ManimColor = None,
        draw_border_animation_config: dict = {},
        fill_animation_config: dict = {},** kwargs
    ):
        # 确保传入的对象是VMobject类型（矢量对象）
        assert isinstance(vmobject, VMobject)
        
        # 为每个子对象创建哈希映射，用于跟踪动画状态
        self.sm_to_index = {hash(sm): 0 for sm in vmobject.get_family()}
        
        # 存储边框宽度、颜色等样式参数
        self.stroke_width = stroke_width
        self.stroke_color = stroke_color
        
        # 存储边框和填充动画的配置参数
        self.draw_border_animation_config = draw_border_animation_config
        self.fill_animation_config = fill_animation_config
        
        # 调用父类构造函数，传入基本动画参数
        super().__init__(
            vmobject,
            run_time=run_time,
            rate_func=rate_func,
            **kwargs
        )
        
        # 显式存储mobject引用（虽然父类也有，但这里更清晰）
        self.mobject = vmobject

    def begin(self) -> None:
        """动画开始时的准备工作"""
        # 设置对象为动画状态
        self.mobject.set_animating_status(True)
        
        # 创建轮廓对象（用于绘制边框）
        self.outline = self.get_outline()
        
        # 调用父类的begin方法，完成基础初始化
        super().begin()
        
        # 让原对象与轮廓对象保持样式一致
        self.mobject.match_style(self.outline)

    def finish(self) -> None:
        """动画结束时的清理工作"""
        # 调用父类的finish方法
        super().finish()
        
        # 刷新对象的连接角度，确保动画结束后显示正常
        self.mobject.refresh_joint_angles()

    def get_outline(self) -> VMobject:
        """创建并返回用于绘制边框的轮廓对象"""
        # 复制原始对象作为轮廓基础
        outline = self.mobject.copy()
        
        # 轮廓对象初始时不填充颜色
        outline.set_fill(opacity=0)
        
        # 为轮廓的所有子对象设置描边样式
        for sm in outline.family_members_with_points():
            sm.set_stroke(
                # 使用指定颜色或原对象的描边颜色
                color=self.stroke_color or sm.get_stroke_color(),
                # 设置描边宽度
                width=self.stroke_width,
                # 保持与原对象相同的描边层级（前后关系）
                behind=self.mobject.stroke_behind,
            )
        return outline

    def get_all_mobjects(self) -> list[Mobject]:
        """返回动画中涉及的所有可移动对象"""
        # 除了父类返回的对象外，还包括轮廓对象
        return [*super().get_all_mobjects(), self.outline]

    def interpolate_submobject(
        self,
        submob: VMobject,
        start: VMobject,
        outline: VMobject,
        alpha: float
    ) -> None:
    # 使用整数插值将alpha值(0-1)映射到0和1两个状态，index为状态索引，subalpha为该状态内的进度
    # 当alpha在0-0.5时，index=0；在0.5-1时，index=1
        index, subalpha = integer_interpolate(0, 2, alpha)

    # 当状态切换到1（即alpha超过0.5）且当前子对象尚未更新状态时
        if index == 1 and self.sm_to_index[hash(submob)] == 0:
        # 首次进入填充阶段时，将子对象的数据设置为轮廓对象的数据
            submob.set_data(outline.data)
        # 更新子对象的状态索引，标记为已进入填充阶段
        self.sm_to_index[hash(submob)] = 1

    # 若处于第一个阶段（alpha < 0.5）：绘制边框
        if index == 0:
        # 让子对象部分显示轮廓，从0到subalpha的进度逐步显示完整轮廓
            submob.pointwise_become_partial(outline, 0, subalpha)
    # 若处于第二个阶段（alpha >= 0.5）：填充颜色
        else:
        # 在轮廓和原始状态之间插值过渡，实现从边框到填充的动画效果
            submob.interpolate(outline, start, subalpha)


class Write(DrawBorderThenFill):
    """
    一个用于实现"书写"效果的动画类，继承自DrawBorderThenFill
    能够模拟手写过程，先逐笔绘制轮廓再填充颜色，常用于文字或复杂图形的展示
    """
    def __init__(
        self,
        vmobject: VMobject,
        run_time: float = -1,  # 若为负数，将在后续重新分配
        lag_ratio: float = -1,  # 若为负数，将在后续重新分配
        rate_func: Callable[[float], float] = linear,
        stroke_color: ManimColor = None,
        **kwargs
    ):
        # 如果未指定描边颜色，则使用矢量对象本身的颜色
        if stroke_color is None:
            stroke_color = vmobject.get_color()
        
        # 计算包含点的子对象数量（用于动态调整动画参数）
        family_size = len(vmobject.family_members_with_points())
        
        # 调用父类DrawBorderThenFill的构造函数
        super().__init__(
            vmobject,
            # 计算运行时间：根据子对象数量和用户指定的run_time确定
            run_time=self.compute_run_time(family_size, run_time),
            # 计算延迟比例：控制多个子对象动画的先后顺序间隔
            lag_ratio=self.compute_lag_ratio(family_size, lag_ratio),
            # 设置速率函数为线性（默认匀速动画）
            rate_func=rate_func,
            # 传递描边颜色参数
            stroke_color=stroke_color,** kwargs
        )

    def compute_run_time(self, family_size: int, run_time: float):
        """
    计算动画运行时间
    根据子对象数量和用户指定的运行时间确定最终动画时长
    
    参数:
        family_size: 包含点的子对象数量
        run_time: 用户指定的运行时间，负数表示使用自动计算值
    """
        # 如果用户未指定有效运行时间（为负数）
        if run_time < 0:
             # 子对象数量少于15个时，运行时间为1秒，否则为2秒
            return 1 if family_size < 15 else 2
        # 如果用户指定了有效运行时间，则直接使用该值
        return run_time

    def compute_lag_ratio(self, family_size: int, lag_ratio: float):
        """
    计算延迟比例
    控制多个子对象动画的先后启动间隔，使动画更自然
    
    参数:
        family_size: 包含点的子对象数量
        lag_ratio: 用户指定的延迟比例，负数表示使用自动计算值
    """
        # 如果用户未指定有效延迟比例（为负数）
        if lag_ratio < 0:
            # 计算延迟比例：取(4/(子对象数量+1))和0.2中的较小值
            # 确保延迟不会过大，同时随对象复杂度动态调整
            return min(4.0 / (family_size + 1.0), 0.2)
        # 如果用户指定了有效延迟比例，则直接使用该值
        return lag_ratio


class ShowIncreasingSubsets(Animation):
    """
    一个用于逐步显示组中子对象的动画类
    继承自Animation基类，实现按顺序逐个显示组内元素的效果
    """
    def __init__(
        self,
        group: Mobject,
        int_func: Callable[[float], float] = np.round,
        suspend_mobject_updating: bool = False,** kwargs
    ):
        # 存储组中所有子对象的列表
        self.all_submobs = list(group.submobjects)
        # 用于将浮点数转换为整数的函数，默认使用numpy的四舍五入
        self.int_func = int_func
        # 调用父类构造函数，传入组对象和其他参数
        super().__init__(
            group,
            suspend_mobject_updating=suspend_mobject_updating,
            **kwargs
        )

    def interpolate_mobject(self, alpha: float) -> None:
        """根据动画进度更新组中显示的子对象"""
        # 获取子对象的总数
        n_submobs = len(self.all_submobs)
        # 应用速率函数处理动画进度（alpha范围为0到1）
        alpha = self.rate_func(alpha)
        # 根据进度计算当前应显示的子对象数量索引
        # alpha * n_submobs将进度映射到0到n_submobs范围，再转换为整数
        index = int(self.int_func(alpha * n_submobs))
        # 更新显示的子对象列表
        self.update_submobject_list(index)

    def update_submobject_list(self, index: int) -> None:
        """根据索引更新组中显示的子对象"""
        # 设置组只显示前index个子对象（切片操作[:index]）
        self.mobject.set_submobjects(self.all_submobs[:index])


class ShowSubmobjectsOneByOne(ShowIncreasingSubsets):
    """
    一个逐个显示组中子对象的动画类，继承自ShowIncreasingSubsets
    与父类不同，该类每次只显示一个子对象，而不是累积显示所有子对象
    """
    def __init__(
        self,
        group: Mobject,
        int_func: Callable[[float], float] = np.ceil,
        **kwargs
    ):
        # 调用父类构造函数，使用np.ceil作为默认的整数转换函数
        # np.ceil确保进度到达阈值时向上取整，保证每个对象完整显示
        super().__init__(group, int_func=int_func, **kwargs)

    def update_submobject_list(self, index: int) -> None:
        """
        重写父类方法，实现每次只显示一个子对象的逻辑
        而非累积显示所有之前的子对象
        """
        # 将索引限制在有效范围内[0, 子对象总数-1]
        # 防止索引越界，确保即使计算出的index超出范围也能正常工作
        index = int(clip(index, 0, len(self.all_submobs) - 1))
        
        # 当索引为0时，不显示任何子对象
        if index == 0:
            self.mobject.set_submobjects([])
        # 当索引大于0时，只显示对应位置的一个子对象
        # index-1是因为索引从1开始对应第一个子对象
        else:
            self.mobject.set_submobjects([self.all_submobs[index - 1]])


class AddTextWordByWord(ShowIncreasingSubsets):
    """
    一个逐词显示文本的动画类，继承自ShowIncreasingSubsets
    专门用于StringMobject，实现文本内容按单词逐个出现的累积显示效果
    """
    def __init__(
        self,
        string_mobject: StringMobject,
        time_per_word: float = 0.2,  # 每个单词的显示时间
        run_time: float = -1.0,      # 总动画时间，负数表示自动计算
        rate_func: Callable[[float], float] = linear,  # 速率函数，默认匀速
        **kwargs
    ):
        # 确保输入对象是StringMobject类型（Manim中处理文本的对象）
        assert isinstance(string_mobject, StringMobject)
        
        # 将文本对象按单词分组，构建分组的mobject
        grouped_mobject = string_mobject.build_groups()
        
        # 如果未指定总运行时间（为负数），则根据单词数量和每个单词的时间计算总时间
        if run_time < 0:
            run_time = time_per_word * len(grouped_mobject)
        
        # 调用父类构造函数，传入分组对象和动画参数
        super().__init__(
            grouped_mobject,
            run_time=run_time,
            rate_func=rate_func,** kwargs
        )
        
        # 保存原始文本对象的引用
        self.string_mobject = string_mobject

    def clean_up_from_scene(self, scene: Scene) -> None:
        """
        动画结束后从场景中清理临时对象，添加最终文本对象
        重写父类方法，确保场景中最终显示的是完整文本对象
        """
        # 从场景中移除动画过程中使用的分组对象
        scene.remove(self.mobject)
        
        # 如果不是移除动画（即普通的显示动画），则将完整文本对象添加到场景
        if not self.is_remover():
            scene.add(self.string_mobject)
