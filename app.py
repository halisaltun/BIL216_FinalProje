import streamlit as st
import pandas as pd
import json
import os
import time
from datetime import datetime

# ============ SAYFA YAPILANDIRMASI ============
st.set_page_config(
    page_title="Emo-Challenge 2026",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============ CSS ============
st.markdown("""
<style>
    .stButton > button {
        width: 100%;
        border-radius: 10px;
        font-weight: bold;
    }
    .phase-active {
        background-color: #28a745;
        color: white;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
    }
    .phase-closed {
        background-color: #dc3545;
        color: white;
        padding: 10px;
        border-radius: 10px;
        text-align: center;
    }
    .stDataFrame table {
        background-color: white !important;
        color: #1a1a1a !important;
    }
    .stDataFrame th {
        background-color: #2c3e50 !important;
        color: white !important;
    }
    .stDataFrame td {
        background-color: white !important;
        color: #1a1a1a !important;
    }
</style>
""", unsafe_allow_html=True)

# ============ VERİ YÖNETİM FONKSİYONLARI ============

def init_data_files():
    """Veri dosyalarını başlat"""
    os.makedirs("data", exist_ok=True)
    
    for phase in [1, 2, 3]:
        file_path = f"data/phase{phase}_scores.json"
        if not os.path.exists(file_path):
            initial_data = {
                "scores": [],
                "last_update": datetime.now().isoformat(),
                "total_entries": 0
            }
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(initial_data, f, indent=2)
    
    phase_file = "data/current_phase.txt"
    if not os.path.exists(phase_file):
        with open(phase_file, "w") as f:
            f.write("1")

def get_current_phase():
    """Geçerli fazı oku"""
    try:
        with open("data/current_phase.txt", "r") as f:
            return int(f.read().strip())
    except:
        return 1

def set_current_phase(phase):
    """Aktif fazı değiştir"""
    with open("data/current_phase.txt", "w") as f:
        f.write(str(phase))

def load_scores(phase):
    """Belirli bir fazın skorlarını yükle"""
    file_path = f"data/phase{phase}_scores.json"
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("scores", [])
    except:
        return []

def save_score(phase, group_id, accuracy, algorithm, features):
    """Yeni skoru kaydet"""
    file_path = f"data/phase{phase}_scores.json"
    
    with open(file_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    new_score = {
        "group_id": group_id,
        "accuracy": accuracy,
        "algorithm": algorithm,
        "features": features,
        "timestamp": datetime.now().isoformat(),
        "phase": phase
    }
    
    data["scores"].append(new_score)
    data["total_entries"] = len(data["scores"])
    data["last_update"] = datetime.now().isoformat()
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    
    return True

def clear_phase_data(phase):
    """Belirli bir fazın tüm verilerini sil"""
    file_path = f"data/phase{phase}_scores.json"
    initial_data = {
        "scores": [],
        "last_update": datetime.now().isoformat(),
        "total_entries": 0
    }
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(initial_data, f, indent=2)

def clear_all_data():
    """Tüm fazların verilerini sil"""
    for phase in [1, 2, 3]:
        clear_phase_data(phase)

def get_leaderboard(phase):
    """Leaderboard için veriyi hazırla"""
    scores = load_scores(phase)
    
    if not scores:
        return pd.DataFrame(columns=["Sıra", "Grup No", "Doğruluk (%)", "Algoritma", "Öznitelikler"])
    
    # Grup bazında en iyi skoru al
    best_scores = {}
    for score in scores:
        group = score["group_id"]
        acc = score["accuracy"]
        if group not in best_scores or acc > best_scores[group]["accuracy"]:
            best_scores[group] = score
    
    df_data = []
    for group, score in best_scores.items():
        df_data.append({
            "Grup No": group,
            "Doğruluk (%)": score["accuracy"],
            "Algoritma": score["algorithm"],
            "Öznitelikler": score["features"][:50] + "..." if len(score["features"]) > 50 else score["features"]
        })
    
    df = pd.DataFrame(df_data)
    if not df.empty:
        df = df.sort_values("Doğruluk (%)", ascending=False).reset_index(drop=True)
        df.index = df.index + 1
        df.insert(0, "Sıra", df.index)
    
    return df

def get_phase_stats(phase):
    """Faz istatistiklerini getir"""
    scores = load_scores(phase)
    if not scores:
        return {"total_entries": 0, "unique_groups": 0, "avg_accuracy": 0, "max_accuracy": 0}
    
    unique_groups = len(set(s["group_id"] for s in scores))
    avg_acc = sum(s["accuracy"] for s in scores) / len(scores)
    max_acc = max(s["accuracy"] for s in scores)
    
    return {
        "total_entries": len(scores),
        "unique_groups": unique_groups,
        "avg_accuracy": round(avg_acc, 2),
        "max_accuracy": max_acc
    }

# ============ ALGORİTMA LİSTELERİ ============
ALGORITHMS = ["Random Forest", "SVM (RBF)", "KNN", "Decision Tree", "MLP (YSA)", 
              "CNN (1D)", "CNN (2D)", "LSTM", "BiLSTM", "GRU", "CNN-LSTM", 
              "Transformer", "ResNet", "XGBoost", "Gradient Boosting", 
              "AdaBoost", "Ensemble", "Transfer Learning", "Karışık", "Diğer"]

# ============ FAZ İÇERİKLERİ ============

def phase1_content():
    st.markdown("### 🎯 Faz 1: Ses Özniteliklerinin Çıkarılması")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.info("""
        **📋 Görev Tanımı:**
        - Verilen ses dosyalarından MFCC, ZCR, Enerji, Pitch vb. zaman düzlemi öznitelikleri çıkarın
        - Çıkardığınız öznitelikleri kullanarak ilk çalışan model. Amaç: Skora dahil olmak.
        - Hangi özniteliklerin duygu tanımada daha etkili olduğunu raporlayın
        
        **📅 Son Teslim Tarihi:** 5 Mayıs 2026, 23:59
        """)
    with col2:
        st.metric("📊 Toplam Başvuru", len(load_scores(1)))
        st.metric("👥 Katılan Grup", get_phase_stats(1)["unique_groups"])

def phase2_content():
    st.markdown("### 🤖 Faz 2: Duygu Sınıflandırma Modeli Eğitimi")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.info("""
        **📋 Görev Tanımı:**
        - Faz 1'de çıkardığınız özniteliklere ek olarak Frekans düzlemi öznitelikleri elde edin
        - Bu yeni özniteliklerle yeni bir sınıflandırıcı eğitin
        - Literatür taraması sonrası yeni öznitelikler ekleyerek model başarımı artırın
        - Amaç: Skoru yukarı çekmek
        
        **📅 Son Teslim Tarihi:** 19 Mayıs 2026, 23:59
        """)
    with col2:
        st.metric("📊 Toplam Başvuru", len(load_scores(2)))
        st.metric("👥 Katılan Grup", get_phase_stats(2)["unique_groups"])

def phase3_content():
    st.markdown("### 🚀 Faz 3: Gerçek Zamanlı Duygu Analizi")
    col1, col2 = st.columns([2, 1])
    with col1:
        st.info("""
        **📋 Görev Tanımı:**
        - Faz 2'deki modelinizi gerçek zamanlı çalışacak şekilde optimize edin
        - Mikrofon veya dosya yükleme ile canlı duygu analizi yapın
        - Web arayüzü ile demo sunun
        - En optimize edilmiş parametreler ve nihai başarı oranı
        
        **📅 Son Teslim Tarihi:** 2 Haziran 2026, 23:59
        """)
    with col2:
        st.metric("📊 Toplam Başvuru", len(load_scores(3)))
        st.metric("👥 Katılan Grup", get_phase_stats(3)["unique_groups"])

def score_input_form(phase_num, placeholder_text):
    """Skor giriş formu oluştur"""
    with st.form(f"phase{phase_num}_form"):
        col1, col2 = st.columns(2)
        with col1:
            group_id = st.text_input("Grup No (Örn: Grup 01)", placeholder="Grup 01")
            algorithm = st.selectbox("Kullanılan Yöntem / Model", ALGORITHMS)
        with col2:
            accuracy = st.number_input("Başarı Oranı (%)", min_value=0.0, max_value=100.0, step=0.1)
            features = st.text_area("Kullanılan Öznitelikler / Detaylar", placeholder=placeholder_text)
        
        submitted = st.form_submit_button("📤 Skoru Gönder", use_container_width=True)
        
        if submitted:
            if not group_id:
                st.error("❌ Lütfen Grup No girin!")
            elif not features:
                st.error("❌ Lütfen öznitelikleri/detayları girin!")
            else:
                save_score(phase_num, group_id, accuracy, algorithm, features)
                st.success(f"✅ Faz {phase_num} skoru kaydedildi! (Grup: {group_id}, Başarı: {accuracy}%)")
                time.sleep(0.5)
                st.rerun()

# ============ ANA UYGULAMA ============

def main():
    init_data_files()
    
    # Header
    st.title("🏆 Emo-Challenge 2026: Duygu Analizi Yarışması")
    st.caption("3 Fazlı Proje Yarışması | BIL216 İşaretler ve Sistemler")
    
    # Sidebar
    with st.sidebar:
        st.header("🎮 Yarışma Kontrol Paneli")
        current_phase = get_current_phase()
        
        # Faz durum göstergeleri
        for phase, name in [(1, "Faz 1"), (2, "Faz 2"), (3, "Faz 3")]:
            status = "✅ AKTİF" if current_phase == phase else "🔒 KAPALI"
            st.markdown(f'<div class="{"phase-active" if current_phase == phase else "phase-closed"}"><strong>{name}</strong><br>{status}</div>', unsafe_allow_html=True)
        
        st.divider()
        
        # ============ YÖNETİCİ PANELİ (SADECE ŞİFRE GİRİNCE GÖRÜNÜR) ============
        with st.expander("🔐 Yönetici Paneli"):
            admin_pass = st.text_input("Yönetici Şifresi", type="password")
            
            if admin_pass == "emo2026admin":
                st.success("✅ Yönetici erişimi onaylandı")
                
                # Faz değiştirme
                st.subheader("📌 Faz Yönetimi")
                new_phase = st.selectbox("Aktif Faz Seç", [1, 2, 3], index=current_phase-1)
                if st.button("⚡ Fazı Değiştir", use_container_width=True):
                    set_current_phase(new_phase)
                    st.success(f"✅ Faz {new_phase} aktif edildi!")
                    st.rerun()
                
                st.divider()
                
                # VERİ SİLME BÖLÜMÜ (SADECE YÖNETİCİ GÖREBİLİR)
                st.warning("⚠️ VERİ SİLME İŞLEMLERİ - DİKKATLİ OLUN!")
                
                col1, col2 = st.columns(2)
                with col1:
                    phase_to_clear = st.selectbox("Silinecek Faz", [1, 2, 3], key="clear_phase")
                    confirm1 = st.checkbox(f"Faz {phase_to_clear} verilerini silmeyi onaylıyorum")
                    if st.button(f"🗑️ Faz {phase_to_clear} Verilerini Sil", type="secondary", use_container_width=True):
                        if confirm1:
                            clear_phase_data(phase_to_clear)
                            st.success(f"✅ Faz {phase_to_clear} verileri silindi!")
                            st.rerun()
                        else:
                            st.error("Lütfen onay kutusunu işaretleyin!")
                
                with col2:
                    confirm_all = st.checkbox("TÜM verileri silmeyi onaylıyorum")
                    if st.button("🔥 TÜM VERİLERİ SİL", type="primary", use_container_width=True):
                        if confirm_all:
                            clear_all_data()
                            st.success("✅ Tüm fazların verileri silindi!")
                            st.rerun()
                        else:
                            st.error("Lütfen onay kutusunu işaretleyin!")
                
                # Veritabanı özeti
                st.divider()
                st.subheader("📊 Veritabanı Özeti")
                for p in [1, 2, 3]:
                    stats = get_phase_stats(p)
                    st.caption(f"Faz {p}: {stats['total_entries']} kayıt, {stats['unique_groups']} grup")
            
            else:
                st.info("🔒 Yönetici paneli için şifre girin")
        
        st.divider()
        
        # Genel istatistikler
        st.header("📊 Genel İstatistikler")
        total_entries = sum(len(load_scores(i)) for i in [1, 2, 3])
        total_groups = len(set(s["group_id"] for i in [1, 2, 3] for s in load_scores(i)))
        st.metric("📝 Toplam Giriş", total_entries)
        st.metric("👥 Toplam Grup", total_groups)
        st.caption(f"🎯 Hedef: 70 grup | {max(0, 70 - total_groups)} eksik")
    
    # ============ ANA SAYFA SEKMELERİ ============
    tab1, tab2, tab3, tab4 = st.tabs(["🎯 Faz 1", "🤖 Faz 2", "🚀 Faz 3", "🏆 Leaderboard"])
    
    with tab1:
        phase1_content()
        if get_current_phase() == 1:
            st.markdown("---")
            st.subheader("📝 Faz 1 Skor Girişi")
            score_input_form(1, "MFCC, ZCR, Enerji, Pitch...")
        else:
            st.warning("🔒 Faz 1 artık aktif değil. Skor girişi yapılamaz!")
    
    with tab2:
        phase2_content()
        if get_current_phase() == 2:
            st.markdown("---")
            st.subheader("📝 Faz 2 Skor Girişi")
            score_input_form(2, "MFCC, ZCR, Pitch, Mel-Spectrogram, Energy...")
        else:
            st.warning("🔒 Faz 2 şu anda aktif değil!")
    
    with tab3:
        phase3_content()
        if get_current_phase() == 3:
            st.markdown("---")
            st.subheader("📝 Faz 3 Skor Girişi")
            score_input_form(3, "CNN katmanları, LSTM unit, dropout, optimizer...")
        else:
            st.warning("🔒 Faz 3 şu anda aktif değil!")
    
    with tab4:
        st.subheader("🏅 Sıralama Tablosu")
        
        phase_choice = st.radio("Leaderboard Seçimi", ["Faz 1", "Faz 2", "Faz 3"], horizontal=True)
        phase_map = {"Faz 1": 1, "Faz 2": 2, "Faz 3": 3}
        selected_phase = phase_map[phase_choice]
        
        df = get_leaderboard(selected_phase)
        stats = get_phase_stats(selected_phase)
        
        if not df.empty:
            st.bar_chart(df.set_index("Grup No")["Doğruluk (%)"])
            st.dataframe(
                df.style.highlight_max(axis=0, subset=["Doğruluk (%)"], color='#90EE90'),
                use_container_width=True,
                height=400
            )
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Toplam Giriş", stats["total_entries"])
            with col2:
                st.metric("👥 Katılan Grup", stats["unique_groups"])
            with col3:
                st.metric("🏆 En Yüksek Başarı", f"{stats['max_accuracy']}%")
        else:
            st.info("💡 Henüz hiç skor girilmemiş. İlk skoru siz girin!")
        
        # Tüm girişlerin detayı
        with st.expander("📋 Tüm Skor Geçmişi (Detaylı)"):
            scores = load_scores(selected_phase)
            if scores:
                df_history = pd.DataFrame([{
                    "Grup No": s["group_id"],
                    "Başarı (%)": s["accuracy"],
                    "Algoritma": s["algorithm"],
                    "Zaman": s["timestamp"][:16]
                } for s in scores])
                st.dataframe(df_history, use_container_width=True)
            else:
                st.caption("Henüz kayıt yok")

if __name__ == "__main__":
    main()
