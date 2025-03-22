from astrbot.api.event import filter, AstrMessageEvent, MessageEventResult
from astrbot.api.message_components import *
from astrbot.api.star import Context, Star, register
from astrbot.api import logger
from astrbot.api.provider import Personality
from astrbot.core.conversation_mgr import Conversation
import random
import os
from datetime import date

'''
luck
├── today
├── card
'''

@register("luck", "kruff", "运势抽卡", "1.0.0")
# 图一乐就好，相信科学，拒绝盲目迷信
class MyPlugin(Star):
    def __init__(self, context: Context):
        super().__init__(context)
        self.persona = self.context.provider_manager.selected_default_persona["prompt"]
    
    @filter.command_group("luck")
    def luck():
        pass
    
    @luck.command("today")
    async def today(self, event: AstrMessageEvent):
        file = "data/plugins/astrbot_plugin_luck/whoami.txt"
        today = date.today().strftime('%Y-%m-%d')
        if not os.path.exists(file):
            with open(file, 'w') as f:
                f.write(today+'\n')
        else:
            with open(file, 'r') as f:
                first_line = f.readlines()[0]
                if first_line != today+'\n':
                    os.remove(file)
                    yield event.plain_result("remove")
                    # 重新创建文件并写入今天的日期
                    with open(file, 'w') as f:
                        f.write(today+'\n')
        with open(file, 'r') as f:
            lines = f.readlines() # {A: (x,y,z)}
            id = event.get_sender_id()
            if len(lines) > 1:
                for line in lines[1:]:
                    if line.split(":")[0] == id:
                        elements = line.split(":")[1].strip("()\n").split(",")
                        chain = [
                            At(qq=event.get_sender_id()),
                            Plain(f" 今天已经测过啦! \n财运: {elements[0]}\n桃花运: {elements[1]}\n事业运: {elements[2]}")        
                        ]
                        yield event.chain_result(chain)
                        return
            cy = random.randint(0, 100)
            thy = random.randint(0, 100)
            syy = random.randint(0, 100)
            llm_response = await self.context.get_using_provider().text_chat(
                prompt=f"{self.persona}。根据财运: {cy}（满分100）, 桃花运: {thy}（满分100）, 事业运: {syy}（满分100），分析今天的运势。",
                session_id=None, # 此已经被废弃
                contexts=[], # 也可以用上面获得的用户当前的对话记录 context
                image_urls=[], # 图片链接，支持路径和网络链接
                func_tool=[], # 当前用户启用的函数调用工具。如果不需要，可以不传
                system_prompt=""  # 系统提示，可以不传
            )
            chain = [
                At(qq=event.get_sender_id()),
                Plain(f" 今天的运势为: \n财运: {cy}\n桃花运: {thy}\n事业运: {syy}")     
            ]
            yield event.chain_result(chain)
            content = llm_response.completion_text.split("\n")
            for text in content:
                if text.strip() != "":
                    yield event.plain_result(text.strip())
            with open(file, 'a') as f:
                f.write(f"{id}:({cy},{thy},{syy})\n")   


    @luck.command("card")
    async def card(self, event: AstrMessageEvent, prompt: str):
        root_path = "data/plugins/astrbot_plugin_luck/pics/"
        files = os.listdir(root_path)
        pic = random.choice(files)
        fine = ["正位", "逆位"]
        turn = random.choice(fine)
        llm_response = await self.context.get_using_provider().text_chat(
            prompt=f"{self.persona}。针对以下事情: {prompt}。分析塔罗牌: {pic[:-5]} {turn}",
            session_id=None, # 此已经被废弃
            contexts=[], # 也可以用上面获得的用户当前的对话记录 context
             image_urls=[], # 图片链接，支持路径和网络链接
            func_tool=[], # 当前用户启用的函数调用工具。如果不需要，可以不传
            system_prompt=""  # 系统提示，可以不传
        )
        chain = [
            Plain(f"{pic[:-5]} {turn}"),
            Image.fromFileSystem(f"{root_path}{pic}")                
        ]
        yield event.chain_result(chain)
        content = llm_response.completion_text.split("\n")
        for text in content:
            if text.strip() != "":
                 yield event.plain_result(text.strip())

    async def terminate(self):
        '''可选择实现 terminate 函数，当插件被卸载/停用时会调用。'''
