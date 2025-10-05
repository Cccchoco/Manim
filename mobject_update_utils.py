# 从__future__导入annotations，支持在类型提示中使用尚未定义的类
from __future__ import annotations

# 导入inspect模块用于检查函数和方法
import inspect

# 从manimlib.constants导入角度单位常量和方向常量
from manimlib.constants import DEG
from manimlib.constants import RIGHT
# 从manimlib.mobject.mobject导入Mobject基类
from manimlib.mobject.mobject import Mobject
# 从manimlib.utils.simple_functions导入clip函数用于值的裁剪
from manimlib.utils.simple_functions import clip

# 导入类型检查相关模块
from typing import TYPE_CHECKING

# 如果是类型检查阶段
if TYPE_CHECKING:
    # 导入所需的类型提示
    from typing import Callable

    import numpy as np

    from manimlib.animation.animation import Animation


def assert_is_mobject_method(method):
    """
    验证输入是否为Mobject对象的方法
    
    Args:
        method: 需要验证的方法
        
    Raises:
        AssertionError: 如果输入不是Mobject的方法
    """
    # 检查是否为方法
    assert inspect.ismethod(method)
    # 获取方法所属的对象
    mobject = method.__self__
    # 检查对象是否为Mobject实例
    assert isinstance(mobject, Mobject)


def always(method, *args, **kwargs):
    """
    为Mobject添加一个更新器，使其始终调用指定方法
    
    该函数会在每一帧都调用指定的方法，可用于创建持续的动画效果
    
    Args:
        method: Mobject的方法
        *args: 传递给方法的位置参数
        **kwargs: 传递给方法的关键字参数
        
    Returns:
        被添加了更新器的Mobject
    """
    # 验证输入是否为Mobject的方法
    assert_is_mobject_method(method)
    # 获取方法所属的Mobject
    mobject = method.__self__
    # 获取方法的函数对象
    func = method.__func__
    # 为Mobject添加更新器，每一帧都调用该方法
    mobject.add_updater(lambda m: func(m, *args, **kwargs))
    return mobject


def f_always(method, *arg_generators, **kwargs):
    """
    功能更强大的always版本，参数由生成器函数提供
    
    与always的区别是：接收的不是固定参数，而是生成参数的函数，
    这样可以在每一帧动态生成不同的参数
    
    Args:
        method: Mobject的方法
        *arg_generators: 生成参数的函数列表
        **kwargs: 传递给方法的关键字参数
        
    Returns:
        被添加了更新器的Mobject
    """
    # 验证输入是否为Mobject的方法
    assert_is_mobject_method(method)
    # 获取方法所属的Mobject
    mobject = method.__self__
    # 获取方法的函数对象
    func = method.__func__

    # 定义更新器函数
    def updater(mob):
        # 调用每个参数生成器，获取当前帧的参数
        args = [
            arg_generator()
            for arg_generator in arg_generators
        ]
        # 调用方法并传递动态生成的参数
        func(mob, *args, **kwargs)

    # 添加更新器
    mobject.add_updater(updater)
    return mobject


def always_redraw(func: Callable[..., Mobject], *args, **kwargs) -> Mobject:
    """
    创建一个Mobject并添加更新器，使其每一帧都重新绘制
    
    适用于需要根据动态变化的数据不断重绘的对象
    
    Args:
        func: 用于创建Mobject的函数
        *args: 传递给创建函数的位置参数
        **kwargs: 传递给创建函数的关键字参数
        
    Returns:
        带有自动重绘更新器的Mobject
    """
    # 初始创建Mobject
    mob = func(*args, **kwargs)
    # 添加更新器：每一帧都用新创建的对象替换当前对象
    mob.add_updater(lambda m: mob.become(func(*args, **kwargs)))
    return mob


def always_shift(
    mobject: Mobject,
    direction: np.ndarray = RIGHT,
    rate: float = 0.1
) -> Mobject:
    """
    为Mobject添加持续移动的更新器
    
    Args:
        mobject: 要移动的Mobject
        direction: 移动方向向量，默认为向右
        rate: 移动速率，单位为单位长度/秒
        
    Returns:
        带有移动更新器的Mobject
    """
    # 添加更新器：根据时间增量(dt)计算移动距离并移动
    mobject.add_updater(
        lambda m, dt: m.shift(dt * rate * direction)
    )
    return mobject


def always_rotate(
    mobject: Mobject,
    rate: float = 20 * DEG,** kwargs
) -> Mobject:
    """
    为Mobject添加持续旋转的更新器
    
    Args:
        mobject: 要旋转的Mobject
        rate: 旋转速率，单位为度/秒，默认为20度/秒
        **kwargs: 传递给rotate方法的其他参数（如旋转轴）
        
    Returns:
        带有旋转更新器的Mobject
    """
    # 添加更新器：根据时间增量(dt)计算旋转角度并旋转
    mobject.add_updater(
        lambda m, dt: m.rotate(dt * rate, **kwargs)
    )
    return mobject


def turn_animation_into_updater(
    animation: Animation,
    cycle: bool = False,** kwargs
) -> Mobject:
    """
    将动画转换为更新器，使动画可以作为持续更新的一部分
    
    这允许将动画集成到更复杂的场景中，而不是作为独立的动画播放
    
    Args:
        animation: 要转换的动画
        cycle: 是否循环播放动画，默认为False（只播放一次）
        **kwargs: 传递给动画的更新速率信息的参数
        
    Returns:
        添加了动画更新器的Mobject
    """
    # 获取动画所属的Mobject
    mobject = animation.mobject
    # 更新动画的速率信息
    animation.update_rate_info(** kwargs)
    # 不暂停Mobject的更新
    animation.suspend_mobject_updating = False
    # 开始动画（执行动画的begin方法）
    animation.begin()
    # 初始化动画的总时间
    animation.total_time = 0

    # 定义更新器函数
    def update(m, dt):
        # 获取动画的运行时间
        run_time = animation.get_run_time()
        # 计算时间比率（已运行时间/总运行时间）
        time_ratio = animation.total_time / run_time
        
        if cycle:
            # 如果循环播放，取时间比率的小数部分
            alpha = time_ratio % 1
        else:
            # 如果不循环，将alpha限制在0到1之间
            alpha = clip(time_ratio, 0, 1)
            # 如果动画完成，执行收尾工作并移除更新器
            if alpha >= 1:
                animation.finish()
                m.remove_updater(update)
                return
        
        # 根据alpha值插值计算动画状态
        animation.interpolate(alpha)
        # 更新动画中的Mobjects
        animation.update_mobjects(dt)
        # 累积动画总时间
        animation.total_time += dt

    # 为Mobject添加更新器
    mobject.add_updater(update)
    return mobject


def cycle_animation(animation: Animation, **kwargs) -> Mobject:
    """
    将动画转换为循环播放的更新器
    
    是turn_animation_into_updater的便捷包装，固定cycle=True
    
    Args:
        animation: 要循环播放的动画
        **kwargs: 传递给turn_animation_into_updater的参数
        
    Returns:
        添加了循环动画更新器的Mobject
    """
    return turn_animation_into_updater(
        animation, cycle=True, **kwargs
    )