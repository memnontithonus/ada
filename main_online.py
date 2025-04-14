from ADA.ADA_Online import ADA
import asyncio

async def main():
    ada = ADA()
    async with asyncio.TaskGroup() as tg:
        tg.create_task(ada.stt())
        input_message = tg.create_task(ada.input_message())
        tg.create_task(ada.send_prompt())
        tg.create_task(ada.tts())
        tg.create_task(ada.play_audio())

        await input_message

if __name__ == "__main__":
    asyncio.run(main())