import asyncio, json
from playwright.async_api import async_playwright
URL="file:///home/user/Doubao/chats/38445857795465986/periodic-wallpaper/index.html"
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path="/usr/local/bin/chromium",args=["--no-sandbox"])
        pg=await b.new_page(viewport={"width":1920,"height":1080})
        await pg.goto(URL,wait_until="load"); await pg.wait_for_timeout(1800)
        data=await pg.evaluate("""()=>{
          const q=z=>{const r=document.querySelector(`.cell[data-z="${z}"]`).getBoundingClientRect();return [Math.round(r.x),Math.round(r.y),Math.round(r.width),Math.round(r.height)]};
          const pt=document.getElementById('pt').getBoundingClientRect();
          const wrap=document.querySelector('.wrap').getBoundingClientRect();
          return {H:q(1),Li:q(3),Na:q(11),K:q(19),Rf:q(104),La:q(57),pt:[Math.round(pt.y),Math.round(pt.height)], wrap:[Math.round(wrap.y),Math.round(wrap.height)]};
        }""")
        print(json.dumps(data,ensure_ascii=False,indent=2)); await b.close()
asyncio.run(main())
