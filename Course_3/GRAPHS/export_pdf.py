import time
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth

def save_buildin_to_pdf(url: str, output_file: str):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 1000}
        )
        page = context.new_page()
        
        # Применяем Stealth (из вашей версии 2.0.2)
        stealth = Stealth()
        stealth.apply_stealth_sync(page)

        print(f"Открываем страницу: {url}")
        page.goto(url, wait_until="networkidle")
        
        # Ждем появления основного контента
        page.wait_for_selector(".notion-page-content, main, .buildin-page-content", timeout=15000)
        time.sleep(2) 

        print("Начинаем умную прокрутку...")

        # JavaScript функция для глубокой прокрутки именно скролл-контейнера
        page.evaluate("""
            async () => {
                // Ищем элемент, который реально скроллится (у него overflow-y: auto или scroll)
                const findScroller = () => {
                    const all = document.querySelectorAll('*');
                    for (let el of all) {
                        if (el.scrollHeight > el.clientHeight && 
                            (getComputedStyle(el).overflowY === 'auto' || getComputedStyle(el).overflowY === 'scroll')) {
                            return el;
                        }
                    }
                    return document.scrollingElement || document.documentElement;
                };

                const scroller = findScroller();
                let lastHeight = scroller.scrollHeight;
                
                // Прокручиваем по чуть-чуть до самого низа
                while (true) {
                    scroller.scrollTop += 800; 
                    await new Promise(r => setTimeout(r, 600)); // Ждем подгрузку
                    
                    let newHeight = scroller.scrollHeight;
                    if (newHeight === lastHeight) {
                        // Попробуем еще раз на случай долгой загрузки
                        await new Promise(r => setTimeout(r, 1500));
                        if (scroller.scrollHeight === lastHeight) break;
                    }
                    lastHeight = newHeight;
                }
                
                // Возвращаемся в начало для правильного рендеринга PDF
                scroller.scrollTop = 0;
            }
        """)

        print("Ждем загрузку всех картинок...")
        # Проверяем, что все картинки на странице реально загружены
        page.evaluate("""
            async () => {
                const imgs = Array.from(document.querySelectorAll('img'));
                await Promise.all(imgs.map(img => {
                    if (img.complete) return;
                    return new Promise((resolve) => {
                        img.onload = img.onerror = resolve;
                    });
                }));
            }
        """)

        # Принудительно отключаем стили печати
        page.emulate_media(media="screen")
        time.sleep(2)

        print("Генерируем PDF...")
        page.pdf(
            path=output_file,
            format="A4",
            print_background=True,
            margin={"top": "1cm", "bottom": "1cm", "left": "1cm", "right": "1cm"},
            prefer_css_page_size=True # Важно для корректного разбиения на страницы
        )

        print(f"✅ Готово! Файл сохранен: {output_file}")
        browser.close()

if __name__ == "__main__":
    target_url = "https://buildin.ai/share/e884b561-80e8-45b9-8300-2ada0c6113ec"
    save_buildin_to_pdf(target_url, "buildin_complete.pdf")