# 从__future__导入annotations，支持在类型注解中使用尚未定义的类
from __future__ import annotations

# 从manimlib的animation模块导入Animation基类和prepare_animation函数
from manimlib.animation.animation import Animation
from manimlib.animation.animation import prepare_animation

# 从mobject模块导入动画构建器和组合对象类
from manimlib.mobject.mobject import _AnimationBuilder  # 动画构建器，用于简化动画创建
from manimlib.mobject.mobject import Group  # 普通对象组合类

# 从vectorized_mobject模块导入矢量对象相关类
from manimlib.mobject.types.vectorized_mobject import VGroup  # 矢量对象组合类
from manimlib.mobject.types.vectorized_mobject import VMobject  # 矢量图形对象基类

# 从工具模块导入插值和贝塞尔曲线相关函数
from manimlib.utils.bezier import integer_interpolate  # 整数插值函数
from manimlib.utils.bezier import interpolate  # 通用插值函数
from manimlib.utils.iterables import remove_list_redundancies  # 移除列表中的冗余元素
from manimlib.utils.simple_functions import clip  # 截断函数，将值限制在指定范围内

# 导入类型检查相关模块
from typing import TYPE_CHECKING, Union, Iterable
# 如果是类型检查阶段，则导入相关类型（避免运行时循环导入问题）
if TYPE_CHECKING:
    # 定义AnimationType类型别名，表示可以是Animation实例或_AnimationBuilder
    AnimationType = Union[Animation, _AnimationBuilder]


DEFAULT_LAGGED_START_LAG_RATIO = 0.05


class AnimationGroup(Animation):
    """
    动画组合类，用于同时或按比例延迟执行多个动画
    继承自Animation基类，是Manim中组合动画的核心类
    """
    def __init__(
        self,
        *args: AnimationType | Iterable[AnimationType],
        run_time: float = -1,  # 若为负数，默认值为所有子动画运行时间的总和
        lag_ratio: float = 0.0,  # 动画之间的延迟比例，0表示同时开始，1表示完全按顺序
        group: Optional[Mobject] = None,  # 可选的预定义动画组对象
        group_type: Optional[type] = None,  # 可选的组类型（如VGroup或Group）
        **kwargs  # 传递给父类Animation的其他参数
    ):
        # 处理输入的动画列表：如果第一个参数是可迭代对象，则将其作为动画列表，否则使用所有参数
        animations = args[0] if isinstance(args[0], Iterable) else args
        
        # 准备所有动画（将动画构建器转换为实际动画对象）
        self.animations = [prepare_animation(anim) for anim in animations]
        
        # 根据延迟比例构建动画的时间安排
        self.build_animations_with_timings(lag_ratio)
        
        # 计算所有动画的最大结束时间（用于确定默认总时长）
        self.max_end_time = max((awt[2] for awt in self.anims_with_timings), default=0)
        
        # 确定总运行时间：若未指定（run_time < 0），则使用最大结束时间
        self.run_time = self.max_end_time if run_time < 0 else run_time
        
        # 保存延迟比例
        self.lag_ratio = lag_ratio
        
        # 收集所有动画涉及的Mobject，并移除重复项
        mobs = remove_list_redundancies([a.mobject for a in self.animations])
        
        # 确定组合动画的组对象（用于统一控制动画的目标）
        if group is not None:
            # 使用预定义的组
            self.group = group
        elif group_type is not None:
            # 使用指定的组类型创建组
            self.group = group_type(*mobs)
        elif all(isinstance(anim.mobject, VMobject) for anim in animations):
            # 若所有动画对象都是矢量对象，使用VGroup
            self.group = VGroup(*mobs)
        else:
            # 否则使用普通Group
            self.group = Group(*mobs)

        # 调用父类构造函数，初始化动画
        super().__init__(
            self.group,
            run_time=self.run_time,
            lag_ratio=lag_ratio,** kwargs
        )

    def get_all_mobjects(self) -> Mobject:
    # 返回该动画组合所包含的所有动画对象的组
        return self.group

def begin(self) -> None:
    # 将组合中的所有对象设置为"正在动画中"状态
    self.group.set_animating_status(True)
    # 对组合中的每个子动画调用begin()方法，初始化它们的动画状态
    for anim in self.animations:
        anim.begin()
    # （注释掉的代码）初始化运行时间，可能是遗留的调试或备用代码
    # self.init_run_time()

    def finish(self) -> None:
    # 当动画组合完成时，将组合对象的动画状态设为False（不再动画中）
        self.group.set_animating_status(False)
    # 遍历所有子动画，并调用它们各自的finish()方法，确保每个子动画都完成收尾工作
    for anim in self.animations:
        anim.finish()

    def clean_up_from_scene(self, scene: Scene) -> None:
        """
        从场景中清理所有子动画的临时对象
        确保动画结束后场景状态正确
    """
        # 遍历所有子动画，调用它们的clean_up_from_scene方法
        for anim in self.animations:
            anim.clean_up_from_scene(scene)

    def update_mobjects(self, dt: float) -> None:
        """
    更新所有子动画中的可移动对象（mobjects）
    通常在每一帧被调用，用于处理动画过程中的状态更新
    
    参数:
        dt: 从上一帧到当前帧的时间间隔（秒）
    """
        # 遍历所有子动画，调用它们的update_mobjects方法
        for anim in self.animations:
            anim.update_mobjects(dt)

    def calculate_max_end_time(self) -> None:
        """
    计算所有子动画的最大结束时间
    用于确定整个动画组的总运行时间
    """
        # 从所有动画的时间三元组中提取结束时间，取最大值作为最大结束时间
        # anims_with_timings格式为(动画对象, 开始时间, 结束时间)
        self.max_end_time = max(
            (awt[2] for awt in self.anims_with_timings),
            default=0,# 如果没有动画，默认最大结束时间为0
        )
        # 如果未指定动画组的运行时间（为负数），则使用最大结束时间作为总运行时间
        if self.run_time < 0:
            self.run_time = self.max_end_time

    def build_animations_with_timings(self, lag_ratio: float) -> None:
        """
        Creates a list of triplets of the form
        (anim, start_time, end_time)
        """
        """
    创建带有时间信息的动画列表，确定每个子动画的开始和结束时间
    
    参数:
        lag_ratio: 动画之间的延迟比例，控制多个动画的启动间隔
                   0表示所有动画同时开始，1表示前一个动画完全结束后下一个才开始
    """
         # 初始化动画时间三元组列表
        self.anims_with_timings = []
        # 当前时间指针，用于计算每个动画的开始时间
        curr_time = 0
        # 遍历所有子动画
        for anim in self.animations:
            # 当前动画的开始时间为当前时间指针
            start_time = curr_time
            # 当前动画的结束时间为开始时间加上动画自身的运行时间
            end_time = start_time + anim.get_run_time()
            # 将动画及其时间信息添加到列表
            self.anims_with_timings.append(
                (anim, start_time, end_time)
            )
            # 计算下一个动画的开始时间
            # 根据lag_ratio在当前动画的开始和结束时间之间插值
            # lag_ratio=0时，下一个动画立即开始；lag_ratio=1时，等当前动画结束后才开始
            # Start time of next animation is based on the lag_ratio
            curr_time = interpolate(
                start_time, end_time, lag_ratio
            )

    def interpolate(self, alpha: float) -> None:
        """
    根据动画组的整体进度，更新所有子动画的进度
    
    参数:
        alpha: 动画组的整体进度（0表示开始，1表示结束）
    """
        # Note, if the run_time of AnimationGroup has been
        # set to something other than its default, these
        # times might not correspond to actual times,
        # e.g. of the surrounding scene.  Instead they'd
        # be a rescaled version.  But that's okay!
        # 注意：如果动画组的run_time被设置为非默认值，
        # 这些时间可能不对应实际场景时间，而是经过缩放的版本，
        # 但这没关系！
    
        # 将整体进度转换为实际时间（基于最大结束时间）
        time = alpha * self.max_end_time
        # 遍历所有带时间信息的动画
        for anim, start_time, end_time in self.anims_with_timings:
            # 计算当前动画的持续时间
            anim_time = end_time - start_time
            if anim_time == 0:
                # 持续时间为0的动画直接使用0作为进度
                sub_alpha = 0
            else:
                # 计算当前动画的相对进度（0到1之间）
                # 使用clip确保进度不会超出有效范围
                sub_alpha = clip((time - start_time) / anim_time, 0, 1)
            # 更新子动画的进度
            anim.interpolate(sub_alpha)


class Succession(AnimationGroup):
    def __init__(
        self,
        *animations: Animation,
        lag_ratio: float = 1.0,
        **kwargs
    ):
        super().__init__(*animations, lag_ratio=lag_ratio, **kwargs)

    def begin(self) -> None:
        assert len(self.animations) > 0
        self.active_animation = self.animations[0]
        self.active_animation.begin()

    def finish(self) -> None:
        self.active_animation.finish()

    def update_mobjects(self, dt: float) -> None:
        self.active_animation.update_mobjects(dt)

    def interpolate(self, alpha: float) -> None:
        index, subalpha = integer_interpolate(
            0, len(self.animations), alpha
        )
        animation = self.animations[index]
        if animation is not self.active_animation:
            self.active_animation.finish()
            animation.begin()
            self.active_animation = animation
        animation.interpolate(subalpha)


class LaggedStart(AnimationGroup):
    def __init__(
        self,
        *animations,
        lag_ratio: float = DEFAULT_LAGGED_START_LAG_RATIO,
        **kwargs
    ):
        super().__init__(*animations, lag_ratio=lag_ratio, **kwargs)


class LaggedStartMap(LaggedStart):
    def __init__(
        self,
        anim_func: Callable[[Mobject], Animation],
        group: Mobject,
        run_time: float = 2.0,
        lag_ratio: float = DEFAULT_LAGGED_START_LAG_RATIO,
        **kwargs
    ):
        anim_kwargs = dict(kwargs)
        anim_kwargs.pop("lag_ratio", None)
        super().__init__(
            *(anim_func(submob, **anim_kwargs) for submob in group),
            run_time=run_time,
            lag_ratio=lag_ratio,
            group=group
        )
