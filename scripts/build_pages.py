#!/usr/bin/env python3
"""Generates the landing pages: index.html (Vietnamese) and en/index.html (English), plus sitemap.xml.

Both languages share one layout: edit COPY below and re-run  python3 scripts/build_pages.py
Privacy, support and 404 are hand-written; this script only refreshes their stylesheet version.
Every link is relative so the site works under https://jarvis219.github.io/tich-tac-tien-site/.
"""
import hashlib, html, json, os, re

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
BASE = "https://jarvis219.github.io/tich-tac-tien-site/"
EMAIL = "jarvis.219.studio@gmail.com"
UPDATED = "2026-10-20"
FONTS = "https://fonts.googleapis.com/css2?family=Baloo+2:wght@600;700;800&family=Nunito:wght@500;700;800&display=swap"
SHOT_W, SHOT_H = 414, 898

COPY = {
    "vi": {
        "path": "", "html_lang": "vi", "og_locale": "vi_VN",
        "title": "Tích Tắc Tiền – Đếm lương theo từng giây trên iPhone",
        "description": "Nhập lương tháng, xem tiền nhảy từng giây. Bấm giờ đi vệ sinh, họp, lướt điện thoại, chờ sếp và nhận hoá đơn có dấu mộc. Miễn phí, offline, không quảng cáo, không tài khoản.",
        "brand": "Tích Tắc Tiền", "alt_brand": "Tick Tock Cash",
        "nav": [("thu-xem", "Thử xem"), ("cach-dung", "Cách dùng"), ("hoa-don", "Hoá đơn"), ("hoi-dap", "Hỏi đáp")],
        "switch": ("English", "en/"),
        "eyebrow": "Bộ đếm lương vô tri cho iPhone & iPad",
        "h1": "Từng giây tích tắc, <mark>từng&nbsp;đồng về&nbsp;túi.</mark>",
        "lead": "Nhập lương tháng, app biến nó thành bộ đếm chạy từng giây. Đi vệ sinh, họp, lướt điện thoại: công ty trả hết, app đếm hết.",
        "store": ("Sắp có trên App Store", "Tải miễn phí"),
        "cta": "Xem tiền nhảy",
        "chips": ["Miễn phí", "Không quảng cáo", "Không cần mạng", "Không tài khoản", "Tiếng Việt & English"],
        "hero_alt": "Màn hình chính Tích Tắc Tiền: 548.775 đ hôm nay, 29,7 đ mỗi giây",
        "ticker": {
            "title": "Thử xem", "tag": "Ví dụ minh hoạ",
            "lead": "Từ lúc bạn mở trang này, một người lương 20 triệu/tháng đã được trả:",
            "rate": "29,7 đ / giây", "tap": "Chạm vào số để đổi sang tô phở, ly trà sữa, hộp mù hay % iPhone.",
            "note": "Đây chỉ là ví dụ chạy trong trình duyệt, không phải lương của bạn. Trang này không lưu và không gửi gì đi.",
            "units": [["đ", 1, "money"], ["tô phở", 50000, "unit"], ["ly trà sữa", 45000, "unit"], ["hộp mù", 550000, "unit"], ["iPhone", 25000000, "pct"]],
            "locale": "vi-VN",
        },
        "how_title": "Dùng thế nào?", "how_lead": "Ba bước. Bước khó nhất là nhớ lương mình bao nhiêu.",
        "steps": [
            ("salary", "Nhập lương tháng", "VND hoặc USD. Chọn giờ làm, ngày làm (bất kỳ ngày nào trong 7 ngày), giờ nghỉ trưa và có nghỉ lễ Việt Nam hay không."),
            ("home", "Nhìn tiền nhảy", "Bộ đếm chạy từng giây: hôm nay, tuần này, tháng này. Nghỉ trưa, hết giờ, cuối tuần thì nó cũng nghỉ."),
            ("receipt", "Bấm giờ, nhận hoá đơn", "Đi vệ sinh, họp, lướt điện thoại, chờ sếp. Bấm Kết thúc là có hoá đơn, dấu mộc đỏ và mưa xu."),
        ],
        "receipt_title": "Hoá đơn cho từng phút “làm việc”",
        "receipt_lead": "Mỗi lần bấm giờ kết thúc bằng một tờ hoá đơn công ty không bao giờ ký. Kèm ảnh 9:16 để đăng Story hay Threads.",
        "receipt": {
            "head": "Họp xong. Công ty trả bạn", "title": "HÓA ĐƠN",
            "rows": [("Họp", "1 giờ"), ("Đơn giá / giây", "29,7 đ")], "total": ("THÀNH TIỀN", "106.920 đ"),
            "stamp": "KPI: NGỒI YÊN", "foot": "Không hoàn tiền. Không hoàn thời gian.",
        },
        "kinds": [("toilet", "Đi vệ sinh", "dấu “ĐÃ XẢ”"), ("dead", "Họp", "dấu “KPI: NGỒI YÊN”"),
                  ("scrolling", "Lướt điện thoại", "dấu “CÔNG TY TÀI TRỢ”"), ("waiting", "Chờ sếp", "dấu “CHỜ DUYỆT”")],
        "late": "<b>Đi trễ?</b> Nhập số phút, app tính luôn khoản bạn không được trả. Trễ 45 phút = mất 80.213 đ. Gần một ly trà sữa. Đau.",
        "pair": [("late", "Đi trễ có giá hẳn hoi"), ("weekly", "Báo cáo tuần: ai trả cho cái gì")],
        "units_title": "Tiền là gì? Là phở.",
        "units_lead": "Chạm vào bộ đếm để đổi đơn vị. Ví dụ một cuộc họp 1 tiếng ở mức 29,7 đ/giây = 106.920 đ, tức là:",
        "units": [("pho", "2,1", "tô phở", "50.000 đ một tô"), ("milktea", "2,4", "ly trà sữa", "45.000 đ một ly"),
                  ("blindbox", "0,19", "hộp mù", "550.000 đ một hộp"), ("iphone", "0,43%", "một chiếc iPhone", "25.000.000 đ một chiếc")],
        "units_fine": "Giá trong app là giá làm tròn cho vui, không phải giá thị trường.",
        "widgets_title": "Tiền nhảy cả ngoài app",
        "widgets_lead": "Widget màn hình chính và màn hình khoá cho biết hôm nay kiếm được bao nhiêu. Đang bấm giờ thì Live Activity và Dynamic Island đếm giúp.",
        "illustration": "Minh hoạ",
        "island": ("Đi vệ sinh", "03:12", "5.702 đ"),
        "w_small": ("Hôm nay", "548.775 đ"), "w_lock": ("Tiền hôm nay", "548.775 đ"),
        "features": [
            ("stickers/kaching", "Widget nhỏ, vừa và màn hình khoá", "Chạm là mở app. iOS làm mới widget vài phút một lần."),
            ("stickers/pending", "Live Activity & Dynamic Island", "Đồng hồ chạy ngay trên màn hình khoá khi đang bấm giờ."),
            ("stickers/certified", "Báo cáo tuần & lịch sử", "Tuần này được trả bao nhiêu cho việc đi vệ sinh. Có số liệu hẳn hoi."),
            ("mascots/holiday", "Nghỉ lễ Việt Nam", "Tết âm lịch, Giỗ Tổ Hùng Vương, 30/4, 1/5, 2/9, 1/1. Ngày lễ bộ đếm nghỉ."),
            ("stickers/offclock", "Biết giờ nghỉ", "Nghỉ trưa, hết giờ, cuối tuần: đồng hồ chạy, tiền thì không."),
        ],
        "more_pair": [("after-hours", "Hết giờ: “Tăng ca không lương”"), ("usd", "Lương đô cũng đếm")],
        "voices_title": "Ba giọng, một sự thật",
        "voices_lead": "Chọn cách app nói chuyện với bạn. Hai ngôn ngữ: Tiếng Việt và English.",
        "voices": [("Lạc quan", "Đồng nào cũng quý. Ly trà sữa lúc nào cũng còn một nửa.", "Hít vào: tiền. Thở ra: cũng tiền."),
                   ("Cà khịa", "Khô khan, hơi mặn, nói hộ điều cả phòng đang nghĩ.", "Sếp nghĩ bạn đang tập trung. Giữ bí mật nhé."),
                   ("Thực tế", "Chỉ có con số. Không cảm xúc, không filter.", "Công ty mua thời gian của bạn. Đây là hoá đơn.")],
        "ipad_title": "Có cả bản iPad",
        "ipad_lead": "Màn hình to hơn, số to hơn, sự thật vẫn vậy. Xoay ngang hay dọc đều được.",
        "ipad_alt": ("Tích Tắc Tiền trên iPad, xoay ngang", "Tích Tắc Tiền trên iPad, xoay dọc"),
        "promise_title": "Lương của bạn không rời khỏi máy",
        "promise": ["Không tài khoản, không máy chủ, không kết nối mạng.", "Không quảng cáo, không theo dõi, không SDK bên thứ ba.",
                    "Gỡ app hoặc “Xoá toàn bộ dữ liệu” trong Cài đặt là sạch."],
        "promise_link": "Đọc chính sách quyền riêng tư",
        "faq_title": "Hỏi nhanh",
        "faq": [
            ("Mỗi giây được tính bao nhiêu tiền?", "Lương tháng chia cho số giây thật sự được trả trong tháng đó. Tháng ít ngày làm thì mỗi giây đáng giá hơn. Bật nghỉ lễ thì ngày lễ không tính."),
            ("Sao bộ đếm đứng im?", "Vì đang nghỉ trưa, hết giờ, cuối tuần hoặc ngày lễ. Ngoài giờ làm, đồng hồ vẫn chạy nhưng tiền thì không."),
            ("Có mất phí không?", "Miễn phí hoàn toàn. Không quảng cáo, không mua trong app, không tài khoản."),
            ("Đây có phải bảng lương thật không?", "Không. Con số chỉ để giải trí, không phải bảng lương hay lời khuyên tài chính."),
        ],
        "faq_more": "Xem thêm câu hỏi ở trang Hỗ trợ",
        "final_title": "Sẵn sàng biết mình đáng giá bao nhiêu mỗi giây?",
        "final_lead": "Tích Tắc Tiền sắp có trên App Store, miễn phí. Trong lúc chờ, bộ đếm phía trên vẫn đang chạy.",
        "footer_privacy": "Quyền riêng tư", "footer_support": "Hỗ trợ", "footer_other": "English",
        "disclaimer": "Con số để giải trí, không phải bảng lương hay lời khuyên tài chính.",
        "skip": "Bỏ qua tới nội dung",
        "shots_note": "",
    },
    "en": {
        "path": "en/", "html_lang": "en", "og_locale": "en_US",
        "title": "Tick Tock Cash – Your salary, ticking by the second on iPhone",
        "description": "Type in your monthly salary and watch it tick up every second. Time toilet breaks, meetings, scrolling and waiting for the boss, and get a stamped receipt. Free, offline, no ads, no account.",
        "brand": "Tick Tock Cash", "alt_brand": "Tích Tắc Tiền",
        "nav": [("try", "Try it"), ("how", "How it works"), ("receipt", "Receipts"), ("faq", "FAQ")],
        "switch": ("Tiếng Việt", "../"),
        "eyebrow": "A deliberately silly pay counter for iPhone & iPad",
        "h1": "Every tick is a few đồng <mark>closer&nbsp;to&nbsp;payday.</mark>",
        "lead": "Type in your monthly salary and the app turns it into a live counter. Toilet breaks, meetings, scrolling: all paid, all counted.",
        "store": ("Coming soon to the App Store", "Free download"),
        "cta": "Watch it tick",
        "chips": ["Free", "No ads", "Works offline", "No account", "English & Tiếng Việt"],
        "hero_alt": "Tick Tock Cash home screen: 548,775 đồng today at 29.7 đồng a second (Vietnamese UI)",
        "ticker": {
            "title": "Try it", "tag": "Example only",
            "lead": "Since you opened this page, someone on 20 million đồng a month has been paid:",
            "rate": "29.7 ₫ / second", "tap": "Tap the number to see it in bowls of pho, cups of milk tea, blind boxes or % of an iPhone.",
            "note": "This is a demo running in your browser, not your salary. The page doesn't save or send anything.",
            "units": [["₫", 1, "money"], ["bowls of pho", 50000, "unit"], ["cups of milk tea", 45000, "unit"], ["blind boxes", 550000, "unit"], ["of an iPhone", 25000000, "pct"]],
            "locale": "en-US",
        },
        "how_title": "How it works", "how_lead": "Three steps. The hardest one is remembering your salary.",
        "steps": [
            ("salary", "Enter your salary", "In VND or USD. Set your hours, your workdays (any of the seven), your lunch break, and whether Vietnamese public holidays count."),
            ("home", "Watch it go up", "A counter that ticks every second: today, this week, this month. It takes lunch, evenings and weekends off too."),
            ("receipt", "Time it, get a receipt", "Toilet, meeting, scrolling, waiting for the boss. Tap End for a receipt, a red rubber stamp and a shower of coins."),
        ],
        "receipt_title": "A receipt for every minute of “work”",
        "receipt_lead": "Every timed session ends with a receipt your company never signed. Plus a 9:16 card for Stories or Threads.",
        "receipt": {
            "head": "Meeting done. The company paid you", "title": "RECEIPT",
            "rows": [("Meeting", "1 hour"), ("Rate / sec", "₫29.7")], "total": ("TOTAL", "₫106,920"),
            "stamp": "KPI: SAT STILL", "foot": "No refunds. No time refunds either.",
        },
        "kinds": [("toilet", "Toilet", "stamped “RELEASED”"), ("dead", "Meeting", "stamped “KPI: SAT STILL”"),
                  ("scrolling", "Scrolling", "stamped “SPONSORED BY THE COMPANY”"), ("waiting", "Waiting for boss", "stamped “PENDING”")],
        "late": "<b>Running late?</b> Type the minutes and the app prices what you didn't get paid. 45 minutes late = 80,213 đồng gone. Nearly a milk tea. Ouch.",
        "pair": [("late", "Being late has a price tag"), ("weekly", "Weekly report: who paid for what")],
        "units_title": "Money is just pho with extra steps",
        "units_lead": "Tap the counter to change units. One hour-long meeting at 29.7 đồng a second is 106,920 đồng, which is:",
        "units": [("pho", "2.1", "bowls of pho", "₫50,000 a bowl"), ("milktea", "2.4", "cups of milk tea", "₫45,000 a cup"),
                  ("blindbox", "0.19", "blind boxes", "₫550,000 a box"), ("iphone", "0.43%", "of an iPhone", "₫25,000,000 each")],
        "units_fine": "Prices in the app are rounded for the joke, not market prices. USD salaries use dollar prices.",
        "widgets_title": "It keeps ticking outside the app",
        "widgets_lead": "Home-screen and lock-screen widgets show today's pay. While a session runs, a Live Activity and the Dynamic Island keep count for you.",
        "illustration": "Illustration",
        "island": ("Toilet", "03:12", "₫5,702"),
        "w_small": ("Today", "₫548,775"), "w_lock": ("Today's pay", "₫548,775"),
        "features": [
            ("stickers/kaching", "Small, medium and lock-screen widgets", "Tap to open the app. iOS refreshes widgets every few minutes."),
            ("stickers/pending", "Live Activity & Dynamic Island", "The session timer right on your lock screen."),
            ("stickers/certified", "Weekly report & history", "How much you got paid to go to the toilet this week. With numbers."),
            ("mascots/holiday", "Vietnamese public holidays", "Lunar Tết, Hùng Kings' day, 30/4, 1/5, 2/9 and 1/1. The counter takes them off."),
            ("stickers/offclock", "Knows when you're off", "Lunch, evenings, weekends: the clock runs, the money doesn't."),
        ],
        "more_pair": [("after-hours", "After hours: “unpaid overtime”"), ("usd", "Paid in dollars? Also counted")],
        "voices_title": "Three voices, one truth",
        "voices_lead": "Pick how the app talks to you. In English or Tiếng Việt.",
        "voices": [("Optimistic", "Every đồng is a win. Glass half full of milk tea.", "Breathe in: money. Breathe out: also money."),
                   ("Sarcastic", "Dry, a little salty, says what everyone's thinking.", "Your boss thinks you're focused. Let's keep it that way."),
                   ("Realistic", "Just the numbers. No feelings, no filter.", "The company buys your time. This is the receipt.")],
        "ipad_title": "On iPad too",
        "ipad_lead": "Bigger screen, bigger number, same truth. Landscape or portrait.",
        "ipad_alt": ("Tick Tock Cash on iPad in landscape (Vietnamese UI)", "Tick Tock Cash on iPad in portrait (Vietnamese UI)"),
        "promise_title": "Your salary never leaves your phone",
        "promise": ["No account, no server, no internet connection.", "No ads, no tracking, no third-party SDKs.",
                    "Delete the app or tap “Reset everything” in Settings and it's all gone."],
        "promise_link": "Read the privacy policy",
        "faq_title": "Quick answers",
        "faq": [
            ("How much is a second worth?", "Your monthly salary divided by the seconds you're actually paid for that month. Fewer workdays means each second is worth more. With holidays on, holidays don't count."),
            ("Why did the counter stop?", "Lunch, after hours, the weekend or a public holiday. Off the clock, the timer runs but the money doesn't."),
            ("Does it cost anything?", "It's free. No ads, no in-app purchases, no account."),
            ("Is this my real payroll?", "No. The number is entertainment, not payroll or financial advice."),
        ],
        "faq_more": "More answers on the Support page",
        "final_title": "Ready to find out what a second of you is worth?",
        "final_lead": "Tick Tock Cash is coming soon to the App Store, for free. Meanwhile, the counter up there is still running.",
        "footer_privacy": "Privacy", "footer_support": "Support", "footer_other": "Tiếng Việt",
        "disclaimer": "The number is entertainment, not payroll or financial advice.",
        "skip": "Skip to content",
        "shots_note": "Screenshots show the Vietnamese interface; the app is fully in English too.",
    },
}

CSS_VERSION = hashlib.sha1(open(os.path.join(ROOT, "assets", "style.css"), "rb").read()).hexdigest()[:8]

# Tiny live counter: starts at 0 when the page opens, 29.7 đ a second, tap to change unit. No dependencies.
TICKER_JS = """
(function () {
  var el = document.getElementById("ticker-num"), cfg = JSON.parse(document.getElementById("ticker-cfg").textContent);
  if (!el) return;
  var start = performance.now(), i = 0, RATE = 29.7;
  function fmt(n, d) { return n.toLocaleString(cfg.locale, { minimumFractionDigits: d, maximumFractionDigits: d }); }
  function draw() {
    var amount = RATE * (performance.now() - start) / 1000, u = cfg.units[i], text;
    if (u[2] === "money") text = cfg.locale === "vi-VN" ? fmt(Math.floor(amount), 0) + " đ" : "₫" + fmt(Math.floor(amount), 0);
    else if (u[2] === "pct") text = fmt(amount / u[1] * 100, 4) + "% " + u[0];
    else { var v = amount / u[1]; text = fmt(v, v >= 100 ? 0 : v >= 10 ? 1 : v >= 1 ? 2 : 3) + " " + u[0]; }
    el.textContent = text;
  }
  el.addEventListener("click", function () { i = (i + 1) % cfg.units.length; draw(); });
  draw();
  setInterval(draw, 100);
})();
"""


def esc(s):
    return html.escape(s, quote=True)


def page(lang):
    c = COPY[lang]
    up = "../" if c["path"] else ""
    url = BASE + c["path"]
    other = "en" if lang == "vi" else "vi"
    shot = lambda n: f"{up}assets/screens/{n}.webp"
    t = c["ticker"]

    app_ld = {
        "@context": "https://schema.org", "@type": "MobileApplication",
        "name": c["brand"], "alternateName": c["alt_brand"],
        "operatingSystem": "iOS 17 or later", "applicationCategory": "LifestyleApplication",
        "inLanguage": ["vi", "en"], "description": c["description"], "url": url,
        "image": BASE + f"assets/og-{lang}.png",
        "screenshot": [BASE + f"assets/screens/{n}.webp" for n in ("home", "receipt", "weekly")],
        "offers": {"@type": "Offer", "price": "0", "priceCurrency": "USD"},
        "author": {"@type": "Person", "name": "Jarvis Tran"}, "isAccessibleForFree": True,
    }
    nav = "".join(f'<a href="#{i}">{esc(x)}</a>' for i, x in c["nav"])
    chips = "".join(f"<li>{esc(x)}</li>" for x in c["chips"])
    steps = "".join(f"""
      <li class="step">
        <span class="step-num" aria-hidden="true">{n}</span>
        <div class="phone"><img src="{shot(name)}" width="{SHOT_W}" height="{SHOT_H}" loading="lazy" decoding="async" alt="{esc(title)}"></div>
        <h3>{esc(title)}</h3>
        <p>{esc(body)}</p>
      </li>""" for n, (name, title, body) in enumerate(c["steps"], 1))
    r = c["receipt"]
    rows = "".join(f'<div class="r-row"><span>{esc(a)}</span><span>{esc(b)}</span></div>' for a, b in r["rows"])
    kinds = "".join(f"""
        <li><img src="{up}assets/mascots/{m}.webp" width="58" height="58" alt="" loading="lazy"><span>{esc(name)}<small>{esc(note)}</small></span></li>""" for m, name, note in c["kinds"])
    pair = lambda items: "".join(f"""
        <figure>
          <div class="phone"><img src="{shot(n)}" width="{SHOT_W}" height="{SHOT_H}" loading="lazy" decoding="async" alt="{esc(cap)}"></div>
          <figcaption>{esc(cap)}</figcaption>
        </figure>""" for n, cap in items)
    units = "".join(f"""
      <li><img src="{up}assets/props/{img}.webp" width="96" height="96" alt="" loading="lazy"><b>{esc(v)}</b><span>{esc(name)}</span><small>{esc(price)}</small></li>""" for img, v, name, price in c["units"])
    features = "".join(f"""
        <li><img src="{up}assets/{img}.webp" width="48" height="48" alt="" loading="lazy"><div><b>{esc(title)}</b><span>{esc(body)}</span></div></li>""" for img, title, body in c["features"])
    voices = "".join(f"""
      <li><h3>{esc(name)}</h3><p class="desc">{esc(desc)}</p><blockquote>{esc(line)}</blockquote></li>""" for name, desc, line in c["voices"])
    promise = "".join(f"<li>{esc(x)}</li>" for x in c["promise"])
    faq = "".join(f"""
      <details><summary>{esc(q)}</summary><p>{esc(a)}</p></details>""" for q, a in c["faq"])
    note = f'\n    <p class="fine">{esc(c["shots_note"])}</p>' if c["shots_note"] else ""
    store = f"""<span class="store-soon" role="img" aria-label="{esc(c['store'][0])}"><img src="{up}assets/web/icon.webp" width="34" height="34" alt=""><span><small>{esc(c['store'][1])}</small>{esc(c['store'][0])}</span></span>"""
    cfg = json.dumps({"locale": t["locale"], "units": t["units"]}, ensure_ascii=False)
    title_og = esc(c["title"])

    return f"""<!doctype html>
<html lang="{c['html_lang']}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(c['title'])}</title>
<meta name="description" content="{esc(c['description'])}">
<link rel="canonical" href="{url}">
<link rel="alternate" hreflang="vi" href="{BASE}">
<link rel="alternate" hreflang="en" href="{BASE}en/">
<link rel="alternate" hreflang="x-default" href="{BASE}">
<meta name="theme-color" content="#FFF4DC">
<meta name="robots" content="index, follow, max-image-preview:large">
<meta property="og:type" content="website">
<meta property="og:site_name" content="{esc(c['brand'])}">
<meta property="og:locale" content="{c['og_locale']}">
<meta property="og:locale:alternate" content="{COPY[other]['og_locale']}">
<meta property="og:title" content="{title_og}">
<meta property="og:description" content="{esc(c['description'])}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{BASE}assets/og-{lang}.png">
<meta property="og:image:width" content="1200">
<meta property="og:image:height" content="630">
<meta property="og:image:alt" content="{esc(c['brand'])}">
<meta name="twitter:card" content="summary_large_image">
<meta name="twitter:title" content="{title_og}">
<meta name="twitter:description" content="{esc(c['description'])}">
<meta name="twitter:image" content="{BASE}assets/og-{lang}.png">
<link rel="icon" type="image/png" sizes="32x32" href="{up}assets/favicon-32.png">
<link rel="apple-touch-icon" href="{up}assets/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="{FONTS}" rel="stylesheet">
<link rel="stylesheet" href="{up}assets/style.css?v={CSS_VERSION}">
<script type="application/ld+json">{json.dumps(app_ld, ensure_ascii=False)}</script>
</head>
<body class="landing">
<a class="skip" href="#main">{esc(c['skip'])}</a>
<header class="topbar">
  <div class="topbar-inner">
    <a class="brand" href="./"><img src="{up}assets/web/icon.webp" width="36" height="36" alt=""><span>{esc(c['brand'])}</span></a>
    <nav aria-label="{esc(c['brand'])}">{nav}</nav>
    <a class="lang-switch" href="{c['switch'][1]}" hreflang="{other}" lang="{other}">{esc(c['switch'][0])}</a>
  </div>
</header>

<main id="main">
  <section class="hero">
    <div class="hero-copy">
      <div class="eyebrow"><img class="hero-icon" src="{up}assets/web/icon.webp" width="88" height="88" alt=""><span><span class="name">{esc(c['brand'])}</span>{esc(c['eyebrow'])}</span></div>
      <h1>{c['h1']}</h1>
      <p class="lead">{esc(c['lead'])}</p>
      <div class="cta-row">
        {store}
        <a class="button" href="#{c['nav'][0][0]}">{esc(c['cta'])}</a>
      </div>
      <ul class="chips">{chips}</ul>
    </div>
    <div class="hero-art">
      <div class="phone"><img src="{shot('home')}" width="{SHOT_W}" height="{SHOT_H}" fetchpriority="high" alt="{esc(c['hero_alt'])}"></div>
      <img class="hero-mascot" src="{up}assets/mascots/idle.webp" width="200" height="168" alt="">
      <img class="hero-coin" src="{up}assets/props/coin.webp" width="64" height="64" alt="">
    </div>
  </section>

  <section id="{c['nav'][0][0]}" class="block">
    <h2 class="label green">{esc(t['title'])}</h2>
    <p class="block-lead">{esc(t['lead'])}</p>
    <div class="ticker">
      <div>
        <span class="ticker-tag">{esc(t['tag'])}</span>
        <button class="ticker-num" id="ticker-num" type="button" aria-live="off" title="{esc(t['tap'])}">{'0 đ' if lang == 'vi' else '₫0'}</button>
        <p class="ticker-rate">{esc(t['rate'])}</p>
        <p class="ticker-note">{esc(t['tap'])} {esc(t['note'])}</p>
      </div>
      <img src="{up}assets/mascots/payday.webp" width="170" height="156" alt="" loading="lazy">
    </div>
    <script type="application/json" id="ticker-cfg">{cfg}</script>
    <script>{TICKER_JS}</script>
  </section>

  <section id="{c['nav'][1][0]}" class="block">
    <h2 class="label">{esc(c['how_title'])}</h2>
    <p class="block-lead">{esc(c['how_lead'])}</p>
    <ol class="steps">{steps}
    </ol>{note}
  </section>

  <section id="{c['nav'][2][0]}" class="block">
    <h2 class="label pink">{esc(c['receipt_title'])}</h2>
    <p class="block-lead">{esc(c['receipt_lead'])}</p>
    <div class="showcase">
      <div class="receipt-wrap">
        <img class="coin c1" src="{up}assets/props/coin.webp" width="54" height="54" alt="">
        <div class="receipt" role="img" aria-label="{esc(r['head'])} {esc(r['total'][1])}. {esc(r['stamp'])}">
          <p class="r-head">{esc(r['head'])}</p>
          <div class="r-title">{esc(r['title'])}</div>
          {rows}
          <div class="r-row r-total"><span>{esc(r['total'][0])}</span><span>{esc(r['total'][1])}</span></div>
          <div class="r-foot">{esc(r['foot'])}</div>
          <span class="stamp">{esc(r['stamp'])}</span>
        </div>
        <img class="coin c2" src="{up}assets/props/coin.webp" width="44" height="44" alt="">
      </div>
      <div>
        <ul class="kinds">{kinds}
        </ul>
        <div class="late-note"><img src="{up}assets/mascots/late.webp" width="80" height="54" alt="" loading="lazy"><p>{c['late']}</p></div>
      </div>
    </div>
    <div class="shot-pair">{pair(c['pair'])}
    </div>
  </section>

  <section class="block">
    <h2 class="label lilac">{esc(c['units_title'])}</h2>
    <p class="block-lead">{esc(c['units_lead'])}</p>
    <ul class="units">{units}
    </ul>
    <p class="fine">{esc(c['units_fine'])}</p>
  </section>

  <section class="block">
    <h2 class="label sky">{esc(c['widgets_title'])}</h2>
    <p class="block-lead">{esc(c['widgets_lead'])}</p>
    <div class="widgets">
      <div class="mock-stage" role="img" aria-label="{esc(c['illustration'])}: Dynamic Island, widget">
        <span class="label amber mock-caption">{esc(c['illustration'])}</span>
        <div class="island"><img src="{up}assets/mascots/toilet.webp" width="34" height="34" alt=""><span>{esc(c['island'][0])}</span><span class="t">{esc(c['island'][1])}</span><span class="m">{esc(c['island'][2])}</span></div>
        <div class="widget-row">
          <div class="w-small"><span class="k">{esc(c['w_small'][0])}</span><span class="v">{esc(c['w_small'][1])}</span><img src="{up}assets/mascots/happy.webp" width="54" height="47" alt=""></div>
          <div class="w-lock">{esc(c['w_lock'][0])}<b>{esc(c['w_lock'][1])}</b></div>
        </div>
      </div>
      <ul class="feature-list">{features}
      </ul>
    </div>
    <div class="shot-pair">{pair(c['more_pair'])}
    </div>
  </section>

  <section class="block">
    <h2 class="label amber">{esc(c['voices_title'])}</h2>
    <p class="block-lead">{esc(c['voices_lead'])}</p>
    <ul class="voices">{voices}
    </ul>
  </section>

  <section class="block">
    <h2 class="label pink">{esc(c['ipad_title'])}</h2>
    <p class="block-lead">{esc(c['ipad_lead'])}</p>
    <div class="ipads">
      <figure class="tablet land"><img src="{shot('ipad-landscape')}" width="900" height="675" loading="lazy" decoding="async" alt="{esc(c['ipad_alt'][0])}"></figure>
      <figure class="tablet port"><img src="{shot('ipad-portrait')}" width="675" height="900" loading="lazy" decoding="async" alt="{esc(c['ipad_alt'][1])}"></figure>
    </div>
  </section>

  <section class="block">
    <div class="promise">
      <img src="{up}assets/mascots/sleeping.webp" width="170" height="115" alt="" loading="lazy">
      <div>
        <h2>{esc(c['promise_title'])}</h2>
        <ul>{promise}</ul>
        <a class="button secondary" href="{up}privacy/#{lang}">{esc(c['promise_link'])}</a>
      </div>
    </div>
  </section>

  <section id="{c['nav'][3][0]}" class="block">
    <h2 class="label green">{esc(c['faq_title'])}</h2>
    <div class="faq">{faq}
    </div>
    <p class="more-link"><a href="{up}support/#{lang}">{esc(c['faq_more'])} →</a></p>
  </section>

  <section class="block final">
    <img src="{up}assets/mascots/capitalist.webp" width="152" height="170" alt="" loading="lazy">
    <h2>{esc(c['final_title'])}</h2>
    <p>{esc(c['final_lead'])}</p>
    <div class="cta-row">{store}</div>
  </section>
</main>

<footer>
  <span class="disclaimer">{esc(c['disclaimer'])}</span>
  <nav aria-label="Footer">
    <a href="{up}privacy/#{lang}">{esc(c['footer_privacy'])}</a>
    <a href="{up}support/#{lang}">{esc(c['footer_support'])}</a>
    <a href="{c['switch'][1]}" hreflang="{other}" lang="{other}">{esc(c['footer_other'])}</a>
    <a href="mailto:{EMAIL}?subject={'T%C3%ADch%20T%E1%BA%AFc%20Ti%E1%BB%81n' if lang == 'vi' else 'Tick%20Tock%20Cash'}">{EMAIL}</a>
  </nav>
  © 2026 Jarvis Tran
</footer>
</body>
</html>
"""


if __name__ == "__main__":
    open(os.path.join(ROOT, "index.html"), "w", encoding="utf-8").write(page("vi"))
    os.makedirs(os.path.join(ROOT, "en"), exist_ok=True)
    open(os.path.join(ROOT, "en", "index.html"), "w", encoding="utf-8").write(page("en"))
    for other in ["privacy/index.html", "support/index.html", "404.html"]:
        path = os.path.join(ROOT, other)
        if os.path.exists(path):
            text = re.sub(r'(assets/style\.css)(\?v=[0-9a-f]+)?"', rf'\1?v={CSS_VERSION}"', open(path, encoding="utf-8").read())
            open(path, "w", encoding="utf-8").write(text)
    pages = ["", "en/", "privacy/", "support/"]
    sitemap = "".join(f"  <url><loc>{BASE}{p}</loc><lastmod>{UPDATED}</lastmod></url>\n" for p in pages)
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write(
        f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{sitemap}</urlset>\n')
    print("pages built")
