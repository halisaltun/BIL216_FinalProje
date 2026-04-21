import streamlit as st
import pandas as pd
import json
import os
import time
from datetime import datetime

# Sayfa yapılandırması
st.set_page_config(
    page_title="Emo-Challenge 2026",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS ile özelleştirme
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
    .leaderboard-card {
        background-color: #f8f9fa;
        padding: 20px;
        border-radius: 15px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ============ VERİ YÖNETİM FONKSİYONLARI ============

def init_data_files():
    """Veri dosyalarını başlat"""
    os.makedirs("data", exist_ok=True)
    
    # Faz dosyalarını kontrol et
    for phase in [1, 2, 3]:
        file_path = f"data/phase{phase}_scores.json"
        if not os.path.exists(file_path):
            initial_data = {
                "scores": [],
                "last_update": datetime.now().isoformat(),
                "total_entries": 0
            }
            with open(file_path, "w") as f:
                json.dump(initial_data, f, indent=2)
    
    # Aktif faz dosyası
    phase_file = "data/current_phase.txt"
    if not os.path.exists(phase_file):
        with open(phase_file, "w") as f:
            f.write("1")

def clear_phase_data(phase):
    """Belirli bir fazın tüm verilerini sil"""
    file_path = f"data/phase{phase}_scores.json"
    initial_data = {
        "scores": [],
        "last_update": datetime.now().isoformat(),
        "total_entries": 0
    }
    with open(file_path, "w") as f:
        json.dump(initial_data, f, indent=2)
        

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
        with open(file_path, "r") as f:
            data = json.load(f)
            return data.get("scores", [])
    except:
        return []

def save_score(phase, group_id, accuracy, algorithm, features):
    """Yeni skoru kaydet"""
    file_path = f"data/phase{phase}_scores.json"
    
    # Mevcut verileri oku
    with open(file_path, "r") as f:
        data = json.load(f)
    
    # Yeni skoru ekle
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
    
    # Kaydet
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)
    
    return True

def get_leaderboard(phase):
    """Leaderboard için veriyi hazırla"""
    scores = load_scores(phase)
    
    if not scores:
        return pd.DataFrame(columns=["Sıra", "Grup No", "Doğruluk (%)", "Algoritma", "Öznitelikler", "Giriş Zamanı"])
    
    # Grup bazında en iyi skoru al
    best_scores = {}
    for score in scores:
        group = score["group_id"]
        acc = score["accuracy"]
        if group not in best_scores or acc > best_scores[group]["accuracy"]:
            best_scores[group] = score
    
    # DataFrame oluştur
    df_data = []
    for group, score in best_scores.items():
        df_data.append({
            "Grup No": group,
            "Doğruluk (%)": score["accuracy"],
            "Algoritma": score["algorithm"],
            "Öznitelikler": score["features"][:50] + "..." if len(score["features"]) > 50 else score["features"],
            "Giriş Zamanı": score["timestamp"][:10]
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

# ============ FAZ İÇERİKLERİ ============

def phase1_content():
    """Faz 1: Öznitelik Çıkarma"""
    st.markdown("### 🎯 Faz 1: Ses Özniteliklerinin Çıkarılması")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info("""
        **📋 Görev Tanımı:**
        - Verilen ses dosyalarından MFCC, ZCR, Enerji, Pitch vb gibi zaman düzlemi öznitelikleri çıkarın
        - Çıkardığınız öznitelikleri kullanarak ilk çalışan model. Amaç: Skora dahil olmak.
        - Hangi özniteliklerin duygu tanımada daha etkili olduğunu raporlayın
        
        **📅 Son Teslim Tarihi:** 5 Mayıs 2026, 23:59
        """)
    
    with col2:
        st.metric("📊 Toplam Başvuru", len(load_scores(1)))
        st.metric("👥 Katılan Grup", get_phase_stats(1)["unique_groups"])

def phase2_content():
    """Faz 2: Model Eğitimi"""
    st.markdown("### 🤖 Faz 2: Duygu Sınıflandırma Modeli Eğitimi")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info("""
        **📋 Görev Tanımı:**
        - Faz 1'de çıkardığınız özniteliklere ek olarak Frekans düzlemi öznitelikleri elde edin
        - Bu yeni özniteliklerle yeni bir sınıflandırıcı eğitin
        - Gerekli ise Literatür taraması sonrası yeni öznitelikler ekleyerek model başarımı artırın
        - Amaç: Skoru yukarı çekmek. 
        
        **📅 Son Teslim Tarihi:** 19 Mayıs 2026, 23:59
        """)
    
    with col2:
        st.metric("📊 Toplam Başvuru", len(load_scores(2)))
        st.metric("👥 Katılan Grup", get_phase_stats(2)["unique_groups"])

def phase3_content():
    """Faz 3: Final Sistemi"""
    st.markdown("### 🚀 Faz 3: Gerçek Zamanlı Duygu Analizi")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info("""
        **📋 Görev Tanımı:**
        - Faz 2'deki modelinizi gerçek zamanlı çalışacak şekilde optimize edin
        - Mikrofon veya dosya yükleme ile canlı duygu analizi yapın
        - Web arayüzü ile demo sunun
        - En optimize edilmiş parametreler ve nihai başarı oranı.

        
        **📅 Son Teslim Tarihi:** 2 Haziran 2026, 23:59
        """)
    
    with col2:
        st.metric("📊 Toplam Başvuru", len(load_scores(3)))
        st.metric("👥 Katılan Grup", get_phase_stats(3)["unique_groups"])

# ============ ANA UYGULAMA ============

def main():
    # Veri dosyalarını başlat
    init_data_files()
    
    # Header
    st.title("🏆 Emo-Challenge 2026: Duygu Analizi Yarışması")
    st.caption("3 Fazlı Proje Yarışması | BIL216 İşaretler ve Sistemler")
    
    # Sidebar - Faz Yönetimi
    with st.sidebar:
        st.header("🎮 Yarışma Kontrol Paneli")
        
        current_phase = get_current_phase()
        
        # Faz durum gösterge
        st.markdown(f"""
        <div class="{'phase-active' if current_phase == 1 else 'phase-closed'}">
            <strong>Faz 1</strong><br>
            {'✅ AKTİF' if current_phase == 1 else '🔒 KAPALI'}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="{'phase-active' if current_phase == 2 else 'phase-closed'}">
            <strong>Faz 2</strong><br>
            {'✅ AKTİF' if current_phase == 2 else '🔒 KAPALI'}
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown(f"""
        <div class="{'phase-active' if current_phase == 3 else 'phase-closed'}">
            <strong>Faz 3</strong><br>
            {'✅ AKTİF' if current_phase == 3 else '🔒 KAPALI'}
        </div>
        """, unsafe_allow_html=True)
        
        st.divider()
        
        # Yönetici paneli (şifre korumalı)
        with st.expander("🔐 Yönetici Paneli"):
            admin_pass = st.text_input("Yönetici Şifresi", type="password")
            if admin_pass == "emo2026admin":  # Bu şifreyi değiştirin!
                new_phase = st.selectbox("Aktif Faz Seç", [1, 2, 3], index=current_phase-1)
                if st.button("⚡ Fazı Değiştir"):
                    set_current_phase(new_phase)
                    st.success(f"✅ Faz {new_phase} aktif edildi!")
                    st.rerun()
                
                st.caption("💡 İpucu: Bu şifreyi `.streamlit/secrets.toml` dosyasına taşıyabilirsiniz")
        
        st.divider()
        # VERİ SİLME BÖLÜMÜ
        st.warning("⚠️ VERİ SİLME İŞLEMLERİ - DİKKATLİ OLUN!")
        
        col1, col2 = st.columns(2)
        with col1:
            phase_to_clear = st.selectbox("Silinecek Faz", [1, 2, 3], key="clear_phase")
            if st.button(f"🗑️ Faz {phase_to_clear} Tüm Verileri Sil", type="secondary"):
                confirm = st.checkbox(f"Emin misiniz? Faz {phase_to_clear} tüm veriler silinecek!")
                if confirm:
                    clear_phase_data(phase_to_clear)
                    st.success(f"✅ Faz {phase_to_clear} verileri silindi!")
                    st.rerun()
        
        with col2:
            if st.button("🔥 TÜM FAZLARI TEMİZLE", type="primary"):
                confirm_all = st.checkbox("TÜM veriler kalıcı olarak silinecek! Onaylıyor musunuz?")
                if confirm_all:
                    for p in [1, 2, 3]:
                        clear_phase_data(p)
                    st.success("✅ Tüm fazların verileri silindi!")
                    st.rerun()
        
        st.caption("💡 İpucu: Bu şifreyi `.streamlit/secrets.toml` dosyasına taşıyabilirsiniz")
        
        
        # Genel istatistikler
        st.header("📊 Genel İstatistikler")
        total_entries = sum(len(load_scores(i)) for i in [1, 2, 3])
        total_groups = len(set(
            s["group_id"] for i in [1, 2, 3] 
            for s in load_scores(i)
        ))
        st.metric("📝 Toplam Giriş", total_entries)
        st.metric("👥 Toplam Grup", total_groups)
        st.caption(f"🎯 Hedef: 70 grup | {70 - total_groups} eksik")
    
    # Faz içerik sekmesi
    phase_tab1, phase_tab2, phase_tab3, leaderboard_tab = st.tabs([
        "🎯 Faz 1", "🤖 Faz 2", "🚀 Faz 3", "🏆 Leaderboard"
    ])
    
    with phase_tab1:
        phase1_content()
        
        # Faz 1 skor girişi
        if get_current_phase() == 1:
            st.markdown("---")
            st.subheader("📝 Faz 1 Skor Girişi")
            
            with st.form("phase1_form"):
                col1, col2 = st.columns(2)
                with col1:
                    group_id = st.text_input("Grup No (Örn: Grup 01)", placeholder="Grup 01")
                    algorithm = st.selectbox("Kullanılan Yöntem", ["Random Forest", "SVM (RBF)", "KNN", "Decision Tree", "MLP (YSA)", 
 "CNN (1D)", "CNN (2D)", "LSTM", "BiLSTM", "GRU", "CNN-LSTM", 
 "Transformer", "ResNet", "XGBoost", "Gradient Boosting", 
 "AdaBoost", "Ensemble", "Transfer Learning", "Karışık", "Diğer"])
                with col2:
                    accuracy = st.number_input("Başarı Oranı (%)", min_value=0.0, max_value=100.0, step=0.1)
                    features = st.text_area("Çıkarılan Öznitelikler", placeholder="MFCC, ZCR, Enerji, Pitch...")
                
                submitted = st.form_submit_button("📤 Skoru Gönder", use_container_width=True)
                
                if submitted:
                    if not group_id:
                        st.error("❌ Lütfen Grup No girin!")
                    elif not features:
                        st.error("❌ Lütfen öznitelikleri girin!")
                    else:
                        save_score(1, group_id, accuracy, algorithm, features)
                        st.success(f"✅ Faz 1 skoru kaydedildi! (Grup: {group_id}, Başarı: {accuracy}%)")
                        time.sleep(1)
                        st.rerun()
        else:
            st.warning("🔒 Faz 1 artık aktif değil. Skor girişi yapılamaz!")
    
    with phase_tab2:
        phase2_content()
        
        if get_current_phase() == 2:
            st.markdown("---")
            st.subheader("📝 Faz 2 Skor Girişi")
            
            with st.form("phase2_form"):
                col1, col2 = st.columns(2)
                with col1:
                    group_id = st.text_input("Grup No", placeholder="Grup 01")
                    algorithm = st.selectbox("Model", ["Random Forest", "SVM (RBF)", "KNN", "Decision Tree", "MLP (YSA)", 
 "CNN (1D)", "CNN (2D)", "LSTM", "BiLSTM", "GRU", "CNN-LSTM", 
 "Transformer", "ResNet", "XGBoost", "Gradient Boosting", 
 "AdaBoost", "Ensemble", "Transfer Learning", "Karışık", "Diğer"])
                with col2:
                    accuracy = st.number_input("Doğruluk (%)", min_value=0.0, max_value=100.0, step=0.1)
                    features = st.text_area("Kullanılan Öznitelikler", placeholder="MFCC, ZCR, Pitch...")
                
                submitted = st.form_submit_button("📤 Skoru Gönder", use_container_width=True)
                
                if submitted:
                    if not group_id:
                        st.error("❌ Lütfen Grup No girin!")
                    else:
                        save_score(2, group_id, accuracy, algorithm, features)
                        st.success(f"✅ Faz 2 skoru kaydedildi! (Grup: {group_id}, Doğruluk: {accuracy}%)")
                        st.rerun()
        else:
            st.warning("🔒 Faz 2 şu anda aktif değil!")
    
    with phase_tab3:
        phase3_content()
        
        if get_current_phase() == 3:
            st.markdown("---")
            st.subheader("📝 Faz 3 Skor Girişi")
            
            with st.form("phase3_form"):
                col1, col2 = st.columns(2)
                with col1:
                    group_id = st.text_input("Grup No", placeholder="Grup 01")
                    algorithm = st.selectbox("Model Tipi", ["Random Forest", "SVM (RBF)", "KNN", "Decision Tree", "MLP (YSA)", 
 "CNN (1D)", "CNN (2D)", "LSTM", "BiLSTM", "GRU", "CNN-LSTM", 
 "Transformer", "ResNet", "XGBoost", "Gradient Boosting", 
 "AdaBoost", "Ensemble", "Transfer Learning", "Karışık", "Diğer"])
                with col2:
                    accuracy = st.number_input("Gerçek Zamanlı Başarı (%)", min_value=0.0, max_value=100.0, step=0.1)
                    features = st.text_area("Optimizasyon Detayları", placeholder="Model mimarisi, kullanılan teknikler...")
                
                submitted = st.form_submit_button("📤 Skoru Gönder", use_container_width=True)
                
                if submitted:
                    if not group_id:
                        st.error("❌ Lütfen Grup No girin!")
                    else:
                        save_score(3, group_id, accuracy, algorithm, features)
                        st.success(f"✅ Faz 3 skoru kaydedildi! (Grup: {group_id}, Başarı: {accuracy}%)")
                        st.rerun()
        else:
            st.warning("🔒 Faz 3 şu anda aktif değil!")
    
    with leaderboard_tab:
        st.subheader("🏅 Genel Sıralama")
        
        # Faz seçimi
        phase_choice = st.radio(
            "Leaderboard Seçimi",
            ["Faz 1", "Faz 2", "Faz 3", "Genel Toplam"],
            horizontal=True
        )
        
        if phase_choice == "Faz 1":
            df = get_leaderboard(1)
            stats = get_phase_stats(1)
        elif phase_choice == "Faz 2":
            df = get_leaderboard(2)
            stats = get_phase_stats(2)
        elif phase_choice == "Faz 3":
            df = get_leaderboard(3)
            stats = get_phase_stats(3)
        else:  # Genel Toplam
            # Tüm fazların skorlarını birleştir
            all_scores = []
            for phase in [1, 2, 3]:
                scores = load_scores(phase)
                for s in scores:
                    s["total_score"] = s["accuracy"]  # Basit toplam
                    all_scores.append(s)
            
            # Grup bazında topla
            group_totals = {}
            for s in all_scores:
                group = s["group_id"]
                if group not in group_totals:
                    group_totals[group] = {"total": 0, "phase1": 0, "phase2": 0, "phase3": 0}
                group_totals[group]["total"] += s["accuracy"]
                group_totals[group][f"phase{s['phase']}"] = s["accuracy"]
            
            df_data = []
            for group, scores in group_totals.items():
                df_data.append({
                    "Grup No": group,
                    "Faz 1": scores["phase1"],
                    "Faz 2": scores["phase2"],
                    "Faz 3": scores["phase3"],
                    "Toplam Puan": scores["total"]
                })
            
            df = pd.DataFrame(df_data)
            if not df.empty:
                df = df.sort_values("Toplam Puan", ascending=False).reset_index(drop=True)
                df.index = df.index + 1
                df.insert(0, "Sıra", df.index)
            
            stats = {"unique_groups": len(df_data)}
        
        # Leaderboard gösterimi
        if not df.empty:
            # Bar chart
            chart_col = df.copy()
            if phase_choice == "Genel Toplam":
                st.bar_chart(chart_col.set_index("Grup No")["Toplam Puan"])
            else:
                st.bar_chart(chart_col.set_index("Grup No")["Doğruluk (%)"])
            
            # Tablo
            st.dataframe(
                df.style.highlight_max(axis=0, color='#D4EDDA'),
                use_container_width=True,
                height=400
            )

            st.dataframe(
                df.style.set_properties(**{'background-color': 'white', 'color': 'black'})
                  .highlight_max(axis=0, subset=["Doğruluk (%)"], color='#90EE90'),
                use_container_width=True
)
            
            # İstatistikler
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("📊 Toplam Giriş", stats.get("total_entries", len(df)))
            with col2:
                st.metric("👥 Katılan Grup", stats["unique_groups"])
            with col3:
                if phase_choice != "Genel Toplam":
                    st.metric("📈 Ortalama Başarı", f"{stats.get('avg_accuracy', 0)}%")
            with col4:
                if phase_choice != "Genel Toplam":
                    st.metric("🏆 En Yüksek", f"{stats.get('max_accuracy', 0)}%")
        else:
            st.info("💡 Henüz hiç skor girilmemiş. İlk skoru siz girin!")
        
        # Tüm girişleri göster (detay)
        with st.expander("📋 Tüm Skor Geçmişi"):
            all_scores_data = []
            for phase in [1, 2, 3]:
                scores = load_scores(phase)
                for s in scores:
                    all_scores_data.append({
                        "Faz": phase,
                        "Grup No": s["group_id"],
                        "Başarı (%)": s["accuracy"],
                        "Algoritma": s["algorithm"],
                        "Zaman": s["timestamp"][:16]
                    })
            
            if all_scores_data:
                st.dataframe(pd.DataFrame(all_scores_data), use_container_width=True)
            else:
                st.caption("Henüz kayıt yok")

if __name__ == "__main__":
    main()
