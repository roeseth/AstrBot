from typing import Union, AsyncGenerator
from ..stage import Stage, register_stage
from ..context import PipelineContext
from astrbot.core.platform.astr_message_event import AstrMessageEvent
from astrbot.core.message.message_event_result import MessageEventResult
from astrbot.core import logger
from .strategies.strategy import StrategySelector

@register_stage
class ContentSafetyCheckStage(Stage):
    '''检查内容安全
    
    当前只会检查文本的。
    '''

    async def initialize(self, ctx: PipelineContext):
        config = ctx.astrbot_config['content_safety']
        self.strategy_selector = StrategySelector(config)

    async def process(self, event: AstrMessageEvent, check_text: str = None) -> Union[None, AsyncGenerator[None, None]]:
        '''检查内容安全'''
        text = check_text if check_text else event.get_message_str()
        ok, info = self.strategy_selector.check(text)
        if not ok:
            event.set_result(MessageEventResult().message("你的消息中包含不适当的内容，已被屏蔽。"))
            yield 
            event.stop_event()
            logger.info(f"内容安全检查不通过，原因：{info}")
            return
        event.continue_event()
