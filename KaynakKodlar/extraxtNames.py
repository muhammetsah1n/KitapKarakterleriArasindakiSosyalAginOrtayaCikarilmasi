import fitz  # PDF'ten metin çıkarmak için
import spacy  # spaCy ile kişi adlarını tespit etmek için
import re  # metin temizleme için
from collections import Counter  # sıklık hesabı için

PDF_PATH = "Harry-Potter-and-the-Chamber-of-Secrets.pdf"
OUTPUT_FILE = "characters.txt"

# PDF'ten düz metin elde eder

def read_pdf_text(pdf_path):
    doc = fitz.open(pdf_path)
    return "\n".join(page.get_text() for page in doc)

# İsimleri temizler (unvanları, özel karakterleri vs. kaldırır)

def clean_name(name):

    name = name.strip()

    titles = [
        "Mr.", "Mrs.", "Ms.", "Miss", "Dr.", "Professor", "Prof.", "Sir", "Madam",
        "Lady", "Lord", "Mr", "Mrs", "Ms", "Dr", "Prof",
        "Father", "Mother", "Dad", "Mom", "Mum", "Papa", "Mama",
        "Uncle", "Aunt", "Cousin", "Brother", "Sister", "Son", "Daughter",
        "Grandfather", "Grandmother", "Grandpa", "Grandma",
        "Master", "Seer", "Heir", "Prince", "Princess", "King", "Queen"
    ]

    words = name.split()
    if words and words[0] in titles:
        words = words[1:]
        name = " ".join(words)

    name = re.split(r"['’\".,!?;:()\[\]\-]", name)[0]
    name = re.sub(r"\s+", " ", name).strip()

    if not any(c.isupper() for c in name):
        return ""

    return name

# spaCy ile kişi (PERSON) adlarını çıkarır

def extract_raw_character_names(text):
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    return [ent.text for ent in doc.ents if ent.label_ == "PERSON"]

# 'Harry' varsa ve 'Harry Potter' da varsa 'Harry'yi çıkarır

def remove_subset_names(name_list):
    name_list = sorted(set(name_list), key=lambda x: -len(x))
    result = []
    for name in name_list:
        name_words = set(name.lower().split())
        if not any(
            name_words.issubset(set(longer.lower().split()))
            and len(name_words) < len(longer.split())
            for longer in result
        ):
            result.append(name)
    return result

# Kullanıcıdan isimleri tek tek onaylama girişi alır
def interactive_approval(name_list):
    approved = []
    print("\n⚡ Karakterleri tek tek onayla veya sil (Enter = onayla, n = sil, q = çıkış)\n")
    for name in name_list:
        while True:
            user_input = input(f"Onayla: '{name}' ? (Enter = evet / n = hayır / q = çıkış): ").strip().lower()
            if user_input == '':
                approved.append(name)
                break
            elif user_input == 'n':
                break
            elif user_input == 'q':
                print("⏹ Onaylama işlemi sonlandırıldı.")
                return approved
            else:
                print("Lütfen sadece Enter, 'n' veya 'q' girin.")
    return approved

# Tüm işlemleri sırayla yapan ana fonksiyon
def save_names_to_txt(raw_names, output_path, min_count=10):
    cleaned_names = [clean_name(name) for name in raw_names]
    cleaned_names = list(filter(None, cleaned_names))

    # Sıklığı yeterli olmayanlar atılır
    counts = Counter(cleaned_names)
    frequent_names = [name for name, count in counts.items() if count >= min_count]

    # Alt küme isimleri kaldır
    final_names = remove_subset_names(frequent_names)

    # İki kelimeli isimleri tek kelimeye indir (örn. "Harry Potter" → "Harry")
    processed_names = []
    for name in final_names:
        parts = name.split()
        if len(parts) == 2:
            processed_names.append(parts[0])
        else:
            processed_names.append(name)

    # Tekrarları kaldır
    processed_names = sorted(set(processed_names))

    # Onay ekranı
    approved_names = interactive_approval(processed_names)

    # Dosyaya yaz
    with open(output_path, "w", encoding="utf-8") as f:
        for name in approved_names:
            f.write(name + "\n")

    print(f"\n✅ Onaylanan karakter sayısı: {len(approved_names)}")

# Ana akış
if __name__ == "__main__":
    print("📖 PDF okunuyor...")
    text = read_pdf_text(PDF_PATH)

    print("🔍 Karakter isimleri çıkarılıyor...")
    raw_names = extract_raw_character_names(text)

    print("🧼 Temizleme ve filtreleme işlemi başlıyor...")
    save_names_to_txt(raw_names, OUTPUT_FILE, min_count=10)

    print(f"✅ Temizlenmiş karakter isimleri '{OUTPUT_FILE}' dosyasına yazıldı.")
