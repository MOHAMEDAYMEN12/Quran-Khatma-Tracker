from docx import Document
from docx.shared import Pt, Cm, RGBColor, Inches
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
import copy

doc = Document()

# ─── Page margins ───
for section in doc.sections:
    section.page_width  = Cm(21)
    section.page_height = Cm(29.7)
    section.top_margin    = Cm(2.5)
    section.bottom_margin = Cm(2.5)
    section.left_margin   = Cm(3)
    section.right_margin  = Cm(2.5)

# ─── Styles helper ───
DARK_BLUE = RGBColor(0x1F, 0x38, 0x64)
MID_BLUE  = RGBColor(0x2E, 0x74, 0xB5)
WHITE     = RGBColor(0xFF, 0xFF, 0xFF)
GREEN     = RGBColor(0x19, 0x69, 0x34)
GRAY      = RGBColor(0x40, 0x40, 0x40)
LIGHT_BLUE_BG = RGBColor(0xDB, 0xE5, 0xF1)

def set_cell_bg(cell, hex_color):
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    shd  = OxmlElement('w:shd')
    shd.set(qn('w:val'),   'clear')
    shd.set(qn('w:color'), 'auto')
    shd.set(qn('w:fill'),  hex_color)
    tcPr.append(shd)

def set_cell_border(cell, **kwargs):
    tc   = cell._tc
    tcPr = tc.get_or_add_tcPr()
    tcBorders = OxmlElement('w:tcBorders')
    for edge in ('top','left','bottom','right','insideH','insideV'):
        tag = OxmlElement(f'w:{edge}')
        tag.set(qn('w:val'),  'single')
        tag.set(qn('w:sz'),   '4')
        tag.set(qn('w:color'),'BFBFBF')
        tcBorders.append(tag)
    tcPr.append(tcBorders)

def heading1(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(18)
    p.paragraph_format.space_after  = Pt(6)
    run = p.add_run(text)
    run.bold      = True
    run.font.size = Pt(14)
    run.font.color.rgb = DARK_BLUE
    # bottom border
    pPr  = p._p.get_or_add_pPr()
    pBdr = OxmlElement('w:pBdr')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'),   'single')
    bottom.set(qn('w:sz'),    '6')
    bottom.set(qn('w:space'), '1')
    bottom.set(qn('w:color'), '1F3864')
    pBdr.append(bottom)
    pPr.append(pBdr)
    return p

def heading2(text):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after  = Pt(4)
    run = p.add_run(text)
    run.bold      = True
    run.font.size = Pt(12)
    run.font.color.rgb = MID_BLUE
    return p

def body(text, bold_parts=None):
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(4)
    p.paragraph_format.alignment   = WD_ALIGN_PARAGRAPH.JUSTIFY
    p.add_run(text).font.size = Pt(11)
    return p

def bullet(text):
    p = doc.add_paragraph(style='List Bullet')
    p.paragraph_format.space_after = Pt(3)
    run = p.add_run(text)
    run.font.size = Pt(11)
    return p

def add_table(headers, rows, header_bg='1F3864'):
    tbl = doc.add_table(rows=1+len(rows), cols=len(headers))
    tbl.style = 'Table Grid'
    tbl.alignment = WD_TABLE_ALIGNMENT.CENTER

    # Header row
    hdr_row = tbl.rows[0]
    for i, h in enumerate(headers):
        cell = hdr_row.cells[i]
        cell.text = h
        cell.paragraphs[0].runs[0].bold = True
        cell.paragraphs[0].runs[0].font.color.rgb = WHITE
        cell.paragraphs[0].runs[0].font.size = Pt(10.5)
        cell.paragraphs[0].alignment = WD_ALIGN_PARAGRAPH.CENTER
        set_cell_bg(cell, header_bg)

    # Data rows
    for r_idx, row_data in enumerate(rows):
        row = tbl.rows[r_idx+1]
        for c_idx, val in enumerate(row_data):
            cell = row.cells[c_idx]
            cell.text = val
            cell.paragraphs[0].runs[0].font.size = Pt(10.5)
            set_cell_border(cell)
            if r_idx % 2 == 1:
                set_cell_bg(cell, 'EBF3FB')

    doc.add_paragraph()
    return tbl

def add_info_box(title, content, bg='DBE5F1'):
    """Simple shaded paragraph as info box"""
    tbl = doc.add_table(rows=1, cols=1)
    tbl.style = 'Table Grid'
    cell = tbl.rows[0].cells[0]
    set_cell_bg(cell, bg)
    if title:
        p = cell.add_paragraph()
        r = p.add_run(f"  {title}")
        r.bold = True
        r.font.size = Pt(11)
        r.font.color.rgb = DARK_BLUE
    for line in content:
        p = cell.add_paragraph()
        p.paragraph_format.left_indent = Cm(0.3)
        r = p.add_run(line)
        r.font.size = Pt(10.5)
    doc.add_paragraph()

def page_break():
    doc.add_page_break()

# ═══════════════════════════════════════════════════
#  KAPAK SAYFASI
# ═══════════════════════════════════════════════════
doc.add_paragraph()
doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("🕌")
r.font.size = Pt(36)

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("WEB PROGRAMLAMA DERSİ")
r.bold = True; r.font.size = Pt(14); r.font.color.rgb = DARK_BLUE

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Bilgisayar Mühendisliği Bölümü\nVize Dönemi Proje Çalışması")
r.font.size = Pt(11); r.font.color.rgb = GRAY

doc.add_paragraph()
doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("VİZE DÖNEMİ PROJE DOKÜMANI")
r.bold = True; r.font.size = Pt(12); r.font.color.rgb = MID_BLUE

doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("KUR'AN KERİM HATİM TAKİP\nWEB UYGULAMASI")
r.bold = True; r.font.size = Pt(22); r.font.color.rgb = DARK_BLUE

doc.add_paragraph()

p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Full-Stack Web Projesi — React.js + Node.js")
r.font.size = Pt(12); r.font.color.rgb = GRAY

doc.add_paragraph()
doc.add_paragraph()

# Info table on cover
info_tbl = doc.add_table(rows=5, cols=2)
info_tbl.style = 'Table Grid'
info_tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
labels = ["Öğrenci Adı", "Öğrenci No", "Danışman Hoca", "Ders Adı", "Teslim Tarihi"]
values = ["", "", "", "Web Programlama", "19 Nisan 2026"]
for i, (lbl, val) in enumerate(zip(labels, values)):
    row = info_tbl.rows[i]
    row.cells[0].text = lbl
    row.cells[0].paragraphs[0].runs[0].bold = True
    row.cells[0].paragraphs[0].runs[0].font.size = Pt(11)
    set_cell_bg(row.cells[0], 'DBE5F1')
    row.cells[1].text = val
    if row.cells[1].paragraphs[0].runs:
        row.cells[1].paragraphs[0].runs[0].font.size = Pt(11)

doc.add_paragraph()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Nisan 2026")
r.font.size = Pt(11); r.font.color.rgb = GRAY

page_break()

# ═══════════════════════════════════════════════════
#  İÇİNDEKİLER
# ═══════════════════════════════════════════════════
heading1("İÇİNDEKİLER")
toc_items = [
    ("1.", "Projenin Amacı Nedir?"),
    ("2.", "Projede Kullanılan Teknolojiler Nelerdir?"),
    ("3.", "Projenin Benzer Projelerden Üstünlüğü Nelerdir?"),
    ("4.", "Mevcut Geliştirme Aşaması ve Proje Görselleri"),
]
for num, title in toc_items:
    p = doc.add_paragraph()
    p.paragraph_format.space_after = Pt(6)
    r1 = p.add_run(f"{num}  {title}")
    r1.font.size = Pt(12)
    r1.bold = True
    r1.font.color.rgb = DARK_BLUE

page_break()

# ═══════════════════════════════════════════════════
#  SORU 1 — PROJENIN AMACI
# ═══════════════════════════════════════════════════
heading1("1. PROJENİN AMACI NEDİR?")

body("Bu proje, Kur'an-ı Kerim hatim takibini dijital ortama taşıyan modern bir web uygulamasıdır. Günümüzde pek çok Müslüman, okuduğu Kur'an sayfasını veya ayeti bir kâğıda ya da hafızasına not etmektedir. Bu yöntem; karışıklığa, ilerlemenin unutulmasına ve takip güçlüğüne yol açmaktadır.")

body("Uygulama, bu temel sorunu çözmeyi hedeflemektedir: Kullanıcı nerede kaldığını sistem üzerinden takip eder, doğrudan web sitesi üzerinden Kur'an okur ve istediği ayette \"Buraya kadar okudum\" diyerek ilerlemeyi kaydeder.")

heading2("1.1  Hedef Kullanıcı Kitlesi")
for item in [
    "Kur'an okuma alışkanlığını takip etmek isteyen bireyler",
    "Aile veya arkadaş grubu adına hatim açmak isteyen kullanıcılar",
    "Ramazan ayı gibi özel dönemlerde grup hatmi organize edenler",
    "Türkçe veya Arapça kullanan geniş bir Müslüman kitlesi",
]:
    bullet(item)

doc.add_paragraph()
heading2("1.2  Çözdüğü Temel Problemler")
add_table(
    ["Problem", "Uygulamamızın Çözümü"],
    [
        ["İlerlemenin kâğıda veya hafızaya not edilmesi", "Dijital kayıt — sunucuda kalıcı olarak saklanır"],
        ["Birden fazla hatimi aynı anda takip edememe",  "Sınırsız kişisel ve başkası adına hatim desteği"],
        ["İlerleme yüzdesini manuel hesaplamak",         "6236 ayet üzerinden otomatik % hesaplama"],
        ["Kur'an metnine erişmek için ayrı uygulama",   "Uygulama içi Kur'an okuyucu (Osmanlı hattı)"],
        ["Dil engeli (yalnızca TR veya AR)",             "Anlık Türkçe ↔ Arapça dil değiştirme"],
    ]
)

heading2("1.3  Uygulamanın Ana İş Akışı")
p = doc.add_paragraph()
r = p.add_run("Kayıt Ol  →  Giriş Yap  →  Hatim Aç  →  Kur'an Oku  →  Ayeti İşaretle  →  İlerleme Kaydedilir")
r.bold = True; r.font.size = Pt(11); r.font.color.rgb = DARK_BLUE
p.alignment = WD_ALIGN_PARAGRAPH.CENTER

page_break()

# ═══════════════════════════════════════════════════
#  SORU 2 — TEKNOLOJİLER
# ═══════════════════════════════════════════════════
heading1("2. PROJEDE KULLANILAN TEKNOLOJİLER NELERDİR?")

body("Proje, modern full-stack web geliştirme prensiplerine uygun olarak iki bağımsız katman halinde geliştirilmiştir: Kullanıcıya sunulan arayüz (Frontend) ve veri yönetimi sağlayan sunucu (Backend).")

heading2("2.1  Frontend Teknolojileri")
add_table(
    ["Teknoloji", "Sürüm", "Kullanım Amacı"],
    [
        ["React.js",              "^19", "Bileşen tabanlı kullanıcı arayüzü geliştirme"],
        ["Vite",                  "^8",  "Hızlı geliştirme sunucusu ve paketleme"],
        ["React Router DOM",      "^7",  "Sayfa yönlendirme (SPA)"],
        ["Axios",                 "^1",  "Backend API'ye HTTP istekleri gönderme"],
        ["i18next / react-i18next","^24","Türkçe / Arapça çok dilli destek"],
        ["Vanilla CSS",           "—",   "Özel karanlık tema tasarım sistemi"],
        ["Amiri (Google Fonts)",  "—",   "Kur'an metni için Arap yazı tipi"],
        ["Alquran Cloud API",     "v1",  "Osmanlı hatlı Kur'an metni (harici, ücretsiz)"],
    ]
)

heading2("2.2  Backend Teknolojileri")
add_table(
    ["Teknoloji", "Sürüm", "Kullanım Amacı"],
    [
        ["Node.js",          "^22", "Sunucu taraflı JavaScript ortamı"],
        ["Express.js",       "^5",  "REST API geliştirme ve HTTP sunucusu"],
        ["SQLite3",          "^6",  "Kurulum gerektirmeyen yerleşik veritabanı"],
        ["bcrypt",           "^6",  "Şifrelerin güvenli biçimde hashlenmesi"],
        ["jsonwebtoken",     "^9",  "JWT oturum doğrulama tokenleri"],
        ["cors",             "^2",  "Frontend-Backend kaynak paylaşımı (CORS)"],
        ["dotenv",           "^17", "Ortam değişkenleri (.env) yönetimi"],
        ["nodemon",          "^3",  "Geliştirmede otomatik yeniden başlatma"],
    ]
)

heading2("2.3  REST API Endpoint Listesi")
add_table(
    ["Method", "Endpoint", "Açıklama", "Kimlik Doğrulama"],
    [
        ["POST", "/api/auth/register", "Yeni kullanıcı kaydı",         "—"],
        ["POST", "/api/auth/login",    "Giriş → JWT token alır",       "—"],
        ["GET",  "/api/khatms",        "Kullanıcının tüm hatimleri",   "✓ JWT"],
        ["POST", "/api/khatms",        "Yeni hatim oluşturma",         "✓ JWT"],
        ["PUT",  "/api/khatms/:id",    "Ayet ilerlemesini güncelleme", "✓ JWT"],
    ]
)

heading2("2.4  Sistem Mimarisi")
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("React (Port 5173)   ⇄  REST API  ⇄   Express.js (Port 5000)   ⇄   SQLite DB")
r.bold = True; r.font.size = Pt(11); r.font.color.rgb = DARK_BLUE
doc.add_paragraph()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("AlQuran Cloud API  →  Kur'an Okuyucu (React)")
r.bold = True; r.font.size = Pt(11); r.font.color.rgb = GREEN

page_break()

# ═══════════════════════════════════════════════════
#  SORU 3 — ÜSTÜNLÜKLER
# ═══════════════════════════════════════════════════
heading1("3. PROJENİN BENZER PROJELERDEN ÜSTÜNLÜĞÜ NELERDİR?")

body("Piyasada hatim takibi yapan çeşitli mobil uygulamalar (My Quran, Hatim, Mushaf gibi) bulunmaktadır. Ancak bu uygulamaların çoğu yalnızca mobil platformlara özel, dil desteği kısıtlı veya sosyal hatim özelliğinden yoksundur. Projemiz bu açıkları kapatan, web tabanlı özgün bir çözüm sunmaktadır.")

heading2("3.1  Özellik Karşılaştırma Tablosu")
add_table(
    ["Özellik", "Bizim Uygulamamız", "Rakip Uygulamalar"],
    [
        ["Tarayıcı tabanlı (kurulum yok)",       "✅ Evet",                        "❌ Çoğunlukla mobil uygulama"],
        ["Uygulama içi Kur'an okuyucu",          "✅ Osmanlı hatlı, tam metin",    "⚠️ Ayrı uygulama gerekir"],
        ["Ayete tıklayarak durak kaydetme",      "✅ Tek tıklama + onay dialogu",  "❌ Manuel sayfa/cüz girişi"],
        ["Başkası adına hatim açma",             "✅ Hedef kişi adıyla",           "❌ Sadece kişisel"],
        ["Türkçe ve Arapça dil desteği",         "✅ Anlık geçiş + RTL/LTR",      "⚠️ Çoğunlukla tek dil"],
        ["Ücretsiz ve açık kaynak",              "✅ Tamamen ücretsiz",            "⚠️ Premium özellikler ücretli"],
        ["Renkli ilerleme çubuğu",               "✅ % gösterimli dinamik çubuk",  "⚠️ Basit metin gösterimi"],
    ]
)

heading2("3.2  Teknik Üstünlükler")
add_info_box(
    "🔐  Güvenlik",
    [
        "Şifreler veritabanında hiçbir zaman düz metin olarak saklanmaz.",
        "bcrypt ile hashlenerek korunur. Oturumlar JWT tokenleri ile yönetilir.",
        "Token 24 saat sonra otomatik olarak geçersiz hale gelir.",
    ],
    'DBE5F1'
)
add_info_box(
    "⚡  Performans",
    [
        "Kur'an metni (~5 MB) uygulamaya gömülmez.",
        "Kullanıcı bir sure seçtiğinde yalnızca o surenin verisi API'den çekilir (Lazy Loading).",
        "İlk yükleme süresi minimum düzeyde tutulur.",
    ],
    'E2EFDA'
)
add_info_box(
    "🌍  Erişilebilirlik",
    [
        "Uygulama tarayıcı tabanlıdır; bilgisayar, tablet ve telefon ile kullanılabilir.",
        "Arapça'ya geçildiğinde tüm sayfa otomatik olarak RTL düzenine geçer.",
    ],
    'FFF2CC'
)
add_info_box(
    "📐  Akıllı İlerleme Hesaplama",
    [
        "İlerleme cüz veya sayfa yöntemiyle değil, doğrudan ayet numarası ile hesaplanır.",
        "Kullanıcı sure adı ve ayet numarası seçer; global indeks sistemi otomatik hesaplar.",
    ],
    'DBE5F1'
)

heading2("3.3  Kullanıcı Deneyimi Üstünlükleri")
for item in [
    "Onay Penceresi (Confirmation Dialog): Kullanıcı yanlış ayete tıklarsa onay ile hata geri alınır.",
    "Görsel ilerleme renkleri: 0–50% Mavi | 50–85% Yeşil | 85–100% Sarı",
    "Okunan ayetler Kur'an okuyucuda yeşil renkte vurgulanır.",
    "İki panel yapısı: 'Kendi Hatimlerim' ve 'Başkası Adına', karışıklık önlenir.",
]:
    bullet(item)

page_break()

# ═══════════════════════════════════════════════════
#  SORU 4 — GELİŞTİRME AŞAMASI
# ═══════════════════════════════════════════════════
heading1("4. MEVCUT GELİŞTİRME AŞAMASI VE PROJE GÖRSELLERİ")

heading2("4.1  Genel Durum Tablosu")
add_table(
    ["Modül / Özellik", "Durum", "Tamamlanma"],
    [
        ["Kullanıcı Kaydı ve Girişi (Auth)",  "✅ Tamamlandı", "100%"],
        ["Veritabanı Şeması (SQLite)",         "✅ Tamamlandı", "100%"],
        ["REST API (5 Endpoint)",              "✅ Tamamlandı", "100%"],
        ["Ana Panel (Dashboard)",             "✅ Tamamlandı", "100%"],
        ["Hatim Kartları ve İlerleme Takibi", "✅ Tamamlandı", "100%"],
        ["Kur'an Okuyucu Sayfası",            "✅ Tamamlandı", "100%"],
        ["Ayet Tıklama + Onay Dialogu",       "✅ Tamamlandı", "100%"],
        ["Türkçe / Arapça Dil Desteği",       "✅ Tamamlandı", "100%"],
        ["Sesli Kur'an Okuma",                "📋 Planlandı",  "0%"],
        ["Meal (Anlam) Görüntüleme",          "📋 Planlandı",  "0%"],
    ]
)

add_info_box(
    "📊  Genel Tamamlanma Oranı: %88",
    ["Temel işlevlerin tamamı geliştirilmiş ve çalışır durumdadır.",
     "Kalan işler yalnızca ek/bonus özelliklerden oluşmaktadır."],
    'E2EFDA'
)

heading2("4.2  Proje Dosya Yapısı")
p = doc.add_paragraph()
p.paragraph_format.space_after = Pt(4)
file_tree = """\
uyglama22/
├── backend/
│   ├── server.js        ← Express sunucusu + tüm API endpoint'leri
│   ├── db.js            ← SQLite bağlantısı + tablo tanımlamaları
│   ├── .env             ← PORT=5000, JWT_SECRET
│   ├── database.sqlite  ← Kalıcı veritabanı dosyası
│   └── package.json
│
└── frontend/
    ├── src/
    │   ├── App.jsx         ← Auth, Dashboard, KhatmCard bileşenleri
    │   ├── QuranReader.jsx ← Kur'an okuyucu + ayet işaretleme
    │   ├── surahData.js    ← 114 sure verisi + indeks fonksiyonları
    │   ├── i18n.js         ← TR / AR çeviriler
    │   ├── index.css       ← Karanlık tema
    │   └── main.jsx        ← React giriş noktası
    └── package.json"""
run = p.add_run(file_tree)
run.font.name = "Courier New"
run.font.size = Pt(9)

heading2("4.3  Veritabanı Şeması")
add_table(
    ["Tablo", "Sütun", "Tür", "Açıklama"],
    [
        ["users",  "id",            "INTEGER PK",          "Otomatik kimlik"],
        ["users",  "name",          "TEXT NOT NULL",        "Kullanıcı adı"],
        ["users",  "email",         "TEXT UNIQUE NOT NULL", "E-posta (benzersiz)"],
        ["users",  "password",      "TEXT NOT NULL",        "bcrypt hashlenmiş şifre"],
        ["khatms", "id",            "INTEGER PK",          "Hatim kimliği"],
        ["khatms", "title",         "TEXT",                "Hatim başlığı"],
        ["khatms", "owner_id",      "INTEGER FK",          "Sahibi (users.id)"],
        ["khatms", "target_person", "TEXT",                "Kimin adına (opsiyonel)"],
        ["khatms", "last_ayah",     "INTEGER",             "Son okunan ayet (1–6236)"],
        ["khatms", "type",          "TEXT",                "'self' veya 'other'"],
    ]
)

heading2("4.4  İlerleme Hesaplama Formülü")
add_info_box(
    "📐  Formül",
    [
        "Tamamlanma (%) = (last_ayah / 6236) × 100",
        "",
        "Örnek: Al-i İmrân, Ayet 200",
        "  getAyahIndex(surahId=3, ayah=200)",
        "  = Fâtiha(7) + Bakara(286) + 200 = 493",
        "  → Tamamlanma = (493 / 6236) × 100 ≈ %7.9",
    ],
    'DBE5F1'
)

heading2("4.5  Çalıştırma Komutları")
add_table(
    ["Sunucu", "Klasör", "Komut", "Adres"],
    [
        ["Backend",  "/backend",  "npm run dev", "http://localhost:5000"],
        ["Frontend", "/frontend", "npm run dev", "http://localhost:5173"],
    ]
)

heading2("4.6  Ekran Açıklamaları")
screens = [
    ("Giriş / Kayıt Ekranı",
     "Koyu arka planlı modern tasarım. Ad, e-posta ve şifre alanları. Kayıt ve giriş sayfaları arasında bağlantı mevcuttur."),
    ("Ana Panel (Dashboard)",
     "İki bölüm: 'Dahil Olduğunuz Hatimler' (kişisel) ve 'Diğer Hatimler' (başkası adına). Her kart: hatim adı, % ilerleme, renkli çubuk, son sure/ayet bilgisi, güncelleme arayüzü ve yeşil 'Kur'an'ı Oku' butonu."),
    ("Kur'an Okuyucu Sayfası",
     "Sure seçim menüsü ve ← → gezinme butonları. Ayetler Osmanlı hattıyla RTL düzeninde görüntülenir. Bismillah otomatik eklenir. Okunan ayetler yeşil renkte gösterilir."),
    ("Onay Penceresi (Dialog)",
     "Bir ayete tıklandığında açılır: 'Bu ayeti durak noktası olarak kaydetmek ister misiniz?' — 'Evet, Kaydet' / 'Hayır, İptal' seçenekleri sunar."),
]
for title, desc in screens:
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(8)
    r = p.add_run(f"▸ {title}: ")
    r.bold = True; r.font.size = Pt(11); r.font.color.rgb = MID_BLUE
    r2 = p.add_run(desc)
    r2.font.size = Pt(11)

page_break()

# ═══════════════════════════════════════════════════
#  SONUÇ
# ═══════════════════════════════════════════════════
heading1("SONUÇ VE DEĞERLENDİRME")

body("Vize dönemine kadar projenin temel işlevleri tamamen geliştirilmiş ve çalışır hale getirilmiştir. Kullanıcı kaydı ve girişi, hatim oluşturma ve takibi, Kur'an okuyucu sayfası ile çok dilli destek eksiksiz olarak tamamlanmıştır.")

body("Proje, gerçek bir kullanıcı ihtiyacına yanıt veren, güvenli, erişilebilir ve modern bir web uygulaması olarak hem teknik hem de işlevsel açıdan hazır durumdadır. Final dönemine kadar sesli Kur'an okuma ve meal görüntüleme gibi ek özellikler eklenmesi planlanmaktadır.")

add_info_box(
    "✅  Vize Dönemi İtibariyle Çalışan Özellikler",
    [
        "• Ad, E-posta, Şifre ile güvenli kullanıcı kaydı ve girişi",
        "• Kişisel ve başkası adına sınırsız hatim açma",
        "• Sure ve ayet seçimi ile ilerleme güncelleme",
        "• 6236 ayet üzerinden otomatik yüzde hesaplama",
        "• Kur'an okuyucu — Osmanlı hattı, Bismillah, sure gezinme",
        "• Ayete tıklayarak ilerleme kaydetme + onay penceresi",
        "• Türkçe ↔ Arapça anlık dil değiştirme + RTL/LTR düzeni",
        "• Karanlık tema (Dark Mode) modern arayüz tasarımı",
    ],
    'E2EFDA'
)

doc.add_paragraph()
p = doc.add_paragraph()
p.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = p.add_run("Kur'an Hatim Takip Web Uygulaması  |  Web Programlama Dersi  |  Nisan 2026")
r.font.size = Pt(9); r.font.color.rgb = GRAY

# ═══════════════════════════════════════════════════
#  KAYDET
# ═══════════════════════════════════════════════════
out = r"c:\Users\MOAyman\Desktop\uyglama22\Vize_Proje_Raporu.docx"
doc.save(out)
print(f"✅ Word dosyası oluşturuldu: {out}")
