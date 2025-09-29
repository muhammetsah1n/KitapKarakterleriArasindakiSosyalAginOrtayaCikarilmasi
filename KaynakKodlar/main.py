import fitz  # PDF dosyasını okumak için PyMuPDF kütüphanesi
import itertools  # Karakter çiftlerini oluşturmak için
import networkx as nx  # Sosyal ağ grafiği oluşturmak için
import matplotlib.pyplot as plt  # Grafik çizmek için
import os  # Dosya ve klasör işlemleri için
import re  # Metin içinde karakterleri tanımak için
from collections import defaultdict  # co-occurrence (birlikte geçme) verisi için

# Girdi dosya yolları
PDF_PATH = "Harry-Potter-and-the-Chamber-of-Secrets.pdf"
CHARACTER_FILE = "characters.txt"
OUTPUT_FILE = "output/network_graph_from_txt.png"

# PDF'i okuyup düz metin döner
def read_pdf_text(pdf_path):
    doc = fitz.open(pdf_path)
    return "\n".join(page.get_text() for page in doc)

# Karakter listesini karakter.txt dosyasından yükler
def load_character_list(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return set(line.strip() for line in f if line.strip())

# Paragraflarda aynı anda geçen karakterleri tespit eder
def extract_co_occurrence(paragraphs, known_characters):
    co_occurrence = defaultdict(int)
    for para in paragraphs:
        words = set(re.findall(r"\b\w+\b", para))  # paragraftaki tüm kelimeleri çıkar
        found = {name for name in known_characters if name in words}  # paragrafta geçen karakterler
        for char1, char2 in itertools.combinations(sorted(found), 2):  # her karakter çifti
            co_occurrence[(char1, char2)] += 1  # birlikte geçme sayısını arttır
    return co_occurrence

# Ağı çiz ve kaydet
def draw_graph(co_occurrence, output_path):
    # Kenar renk skalası: zayıf → güçlü (3 seviye renk tanımı)
    color_scale = [
        "#d1e000",  # yeşil
        "#1E00FF",  # mavi
        "#FF0000"   # kırmızı
    ]

    G = nx.Graph()
    for (char1, char2), weight in co_occurrence.items():
        G.add_edge(char1, char2, weight=weight)  # kenarı ekle

    if not G.edges:
        print("❌ Grafik çizilemedi: Kenar bulunamadı.")
        return None

    pos = nx.spring_layout(G, k=5.8)  # düğüm konumları

    edges = list(G.edges(data=True))
    weights = [edata['weight'] for _, _, edata in edges]

    # Kenar ağırlıklarına göre renk seviyeleri
    min_w, max_w = min(weights), max(weights)
    if max_w == min_w:
        bins = [1] * len(weights)
    else:
        bin_edges = [min_w + (max_w - min_w) * i / 3 for i in range(1, 3)]
        bins = [sum(w > edge for edge in bin_edges) for w in weights]

    edges_sorted = sorted(zip(edges, bins), key=lambda x: x[0][2]['weight'])

    plt.figure(figsize=(10,10))
    plt.axis('off')

    # Kenarları çiz
    for ((u, v, edata), bin_idx) in edges_sorted:
        nx.draw_networkx_edges(
            G, pos,
            edgelist=[(u, v)],
            width=4,
            edge_color=color_scale[bin_idx],
            alpha=0.8
        )

    # Düğümleri ve etiketleri çiz
    nx.draw_networkx_nodes(G, pos, node_color="orange", node_size=2000)
    nx.draw_networkx_labels(G, pos, font_size=8)

    # Ağ yoğunluğu ve çapı hesapla
    density = nx.density(G)
    try:
        diameter = nx.diameter(G)
    except nx.NetworkXError:
        diameter = "Tanımsız (Graph bağlı değil)"

    # Kenara yoğunluk ve çap bilgisini yaz
    info_text = f"Density: {density:.4f}\nDiameter: {diameter}"
    plt.text(0.01, 0.99, info_text, transform=plt.gca().transAxes,
             verticalalignment='top', horizontalalignment='left',
             fontsize=12, bbox=dict(facecolor='white', alpha=0.7, boxstyle='round'))

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    plt.savefig(output_path, bbox_inches='tight', pad_inches=0)
    plt.show()

    return G  # grafiği geri döndür (merkezilik için)

# Merkezilik grafikleri çizer (ayrı 3 grafik)
def draw_centrality_bars_separate_figures(G, output_dir):
    import numpy as np
    os.makedirs(output_dir, exist_ok=True)

    # Üç farklı merkezilik ölçütünü hesapla
    degree_centrality = nx.degree_centrality(G)
    betweenness_centrality = nx.betweenness_centrality(G)
    closeness_centrality = nx.closeness_centrality(G)

    nodes = list(G.nodes())
    x = np.arange(len(nodes))
    width = 0.6

    # Derece merkezliği
    plt.figure(figsize=(12,6))
    plt.bar(x, [degree_centrality[n] for n in nodes], width, color='skyblue')
    plt.title("Derece Merkezliği")
    plt.xticks(x, nodes, rotation=45, ha='right', fontsize=10)
    plt.ylabel("Merkezilik Değeri")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "degree_centrality.png"))
    plt.show()

    # Aracılık merkezliği
    plt.figure(figsize=(12,6))
    plt.bar(x, [betweenness_centrality[n] for n in nodes], width, color='salmon')
    plt.title("Aracılık Merkezliği")
    plt.xticks(x, nodes, rotation=45, ha='right', fontsize=10)
    plt.ylabel("Merkezilik Değeri")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "betweenness_centrality.png"))
    plt.show()

    # Yakınlık merkezliği
    plt.figure(figsize=(12,6))
    plt.bar(x, [closeness_centrality[n] for n in nodes], width, color='lightgreen')
    plt.title("Yakınlık Merkezliği")
    plt.xticks(x, nodes, rotation=45, ha='right', fontsize=10)
    plt.ylabel("Merkezilik Değeri")
    plt.tight_layout()
    plt.savefig(os.path.join(output_dir, "closeness_centrality.png"))
    plt.show()

# Ana akış
if __name__ == "__main__":
    print("⏳ PDF okunuyor...")
    text = read_pdf_text(PDF_PATH)

    print("📄 Karakter listesi yükleniyor...")
    characters = load_character_list(CHARACTER_FILE)

    print("🔎 Paragraflar analiz ediliyor...")
    paragraphs = text.split("\n")

    print("📊 İlişkiler çıkarılıyor...")
    co_occurrence = extract_co_occurrence(paragraphs, characters)

    print("🎨 Grafik çiziliyor...")
    G = draw_graph(co_occurrence, OUTPUT_FILE)

    if G is not None:
        print("📊 Merkeziyet grafikleri çiziliyor...")
        draw_centrality_bars_separate_figures(G, output_dir="output/centralities")

    print("✅ İşlem tamamlandı! Çıktı dosyası:", OUTPUT_FILE)
