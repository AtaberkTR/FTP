import pyshark
import pandas as pd
from datetime import datetime

# Ağ trafiğini yakalayacak arayüzü tanımla
INTERFACE = 'eth0'  # Kendi ağ arayüzünüzü burada belirleyin

# Belirli protokolleri yakalamak için bir filtre oluştur (örneğin, HTTP)
capture_filter = 'http'

# Canlı ağ trafiğini izleme
capture = pyshark.LiveCapture(interface=INTERFACE, display_filter=capture_filter)

# Veri saklama için bir DataFrame oluştur
columns = ['Timestamp', 'Source IP', 'Destination IP', 'HTTP Host', 'HTTP Request Path']
df = pd.DataFrame(columns=columns)

# Paketleri analiz et
for packet in capture.sniff_continuously():
    try:
        # Zaman damgasını al
        timestamp = datetime.fromtimestamp(float(packet.sniff_timestamp))

        # Kaynak ve hedef IP adreslerini al
        src_ip = packet.ip.src
        dst_ip = packet.ip.dst

        # HTTP ana bilgisayar ve istek yolunu al
        http_host = packet.http.host
        http_request_path = packet.http.request_path

        # Verileri bir DataFrame satırı olarak ekle
        df = df.append({
            'Timestamp': timestamp,
            'Source IP': src_ip,
            'Destination IP': dst_ip,
            'HTTP Host': http_host,
            'HTTP Request Path': http_request_path
        }, ignore_index=True)

        # Anlık olarak ekrana yazdır
        print(f"[{timestamp}] {src_ip} -> {dst_ip} | Host: {http_host}, Path: {http_request_path}")

    except AttributeError:
        # Paket belirtilen filtreye uymadığında bu hata oluşur, bu yüzden atlıyoruz
        continue

# Sonuçları bir dosyaya kaydet (CSV)
df.to_csv('http_traffic_log.csv', index=False)
print("Veriler 'http_traffic_log.csv' dosyasına kaydedildi.")