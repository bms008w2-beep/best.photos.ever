import streamlit as st
from PIL import Image

# =================================================================
# 1. INITIAL SETTINGS & BULLETPROOF LAYOUT DESIGN (CSS)
# =================================================================
st.set_page_config(page_title="Travel Photos", layout="wide")

st.markdown("""
    <style>
    header, [data-testid="stHeader"] { display: none !important; }
    .stApp { background-color: #FCFBFA; }
    .single-photo-container { max-width: 1330px; margin: 0 auto 60px auto; }
    .header-grid {
        max-width: 1330px;
        margin: 15px auto 20px auto;
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
    }
    .logo-inline-wrapper { display: flex; flex-direction: row; align-items: center; white-space: nowrap; flex-shrink: 0; }
    .site-brand {
        font-weight: bold; color: #000000 !important; font-size: 2.6rem;
        text-decoration: none !important; user-select: none; display: inline-flex; align-items: center; line-height: 1.1;
    }
    .plus-icon {
        font-weight: 300 !important; font-size: 2.4rem; color: #000000 !important;
        text-decoration: none !important; cursor: pointer; transition: color 0.2s;
        margin-left: 15px; display: inline-block; line-height: 1; transform: translateY(-2px);
    }
    .plus-icon:hover { color: #8C8A87 !important; }
    .menu-container { display: flex; flex-direction: column; align-items: flex-end; justify-content: flex-start; flex-grow: 1; padding-top: 8px; }
    .menu-row { display: block; margin-bottom: 6px; font-size: 1.15rem; color: #2C2A29; line-height: 1.3; text-align: right; }
    .menu-link {
        color: #2C2A29 !important; text-decoration: none !important;
        border-bottom: 1px dotted #2C2A29; margin-left: 20px; cursor: pointer; display: inline-block; transition: opacity 0.2s;
    }
    .menu-link:hover { opacity: 0.6; }
    .active-link { font-weight: bold !important; border-bottom: 2px solid #000000 !important; color: #000000 !important; }
    .photo-title { color: #000000; font-size: 2rem; font-weight: bold; margin-top: 20px; margin-bottom: 2px; letter-spacing: -0.5px; }
    .photo-meta { color: #8C8A87; font-size: 1.1rem; margin-bottom: 15px; }
    .photo-comment { color: #333333; font-size: 0.95rem; line-height: 1.6; }
    .upload-form-wrapper { max-width: 1330px; margin: 10px auto 30px auto; }
    </style>
""", unsafe_allow_html=True)

# =================================================================
# 2. STATE MANAGEMENT (Photo List Initialized as Empty)
# =================================================================
if "photo_list" not in st.session_state:
    st.session_state.photo_list = [] # ここを空のリストにしました

if "show_form" not in st.session_state: st.session_state.show_form = False
if "is_authenticated" not in st.session_state: st.session_state.is_authenticated = False
if "selected_cat" not in st.session_state: st.session_state.selected_cat = "ALL"
if "selected_year" not in st.session_state: st.session_state.selected_year = "ALL"

params = st.query_params
if "cat" in params: st.session_state.selected_cat = params["cat"]
if "year" in params: st.session_state.selected_year = params["year"]
if "toggle" in params:
    st.session_state.show_form = not st.session_state.show_form
    if not st.session_state.show_form: st.session_state.is_authenticated = False
    st.query_params.clear()
    st.rerun()

# =================================================================
# 3. MENU GENERATION (Only items with photos appear)
# =================================================================
categories = sorted(list(set(p["category"] for p in st.session_state.photo_list if p["category"])))
years = sorted(list(set(p["year"] for p in st.session_state.photo_list if p["year"])), reverse=True)

cat_html = "".join([f'<a class="menu-link {"active-link" if st.session_state.selected_cat == c else ""}" href="?cat={c}" target="_self">{c}</a>' for c in categories])
year_html = "".join([f'<a class="menu-link {"active-link" if st.session_state.selected_year == y else ""}" href="?year={y}" target="_self">{y}</a>' for y in years])

st.markdown(f'''
    <div class="header-grid">
        <div class="logo-inline-wrapper">
            <a class="site-brand" href="?cat=ALL&year=ALL" target="_self">Best Photos</a>
            <a class="plus-icon" href="?toggle=1" target="_self">＋</a>
        </div>
        <div class="menu-container">
            <div class="menu-row">{cat_html}</div>
            <div class="menu-row">{year_html}</div>
        </div>
    </div>
''', unsafe_allow_html=True)

# =================================================================
# 4. UPLOAD FORM
# =================================================================
if st.session_state.show_form:
    col2 = st.columns([1, 2, 1])[1]
    with col2:
        st.markdown('<div class="upload-form-wrapper">', unsafe_allow_html=True)
        if not st.session_state.is_authenticated:
            st.subheader("Administrator Authentication")
            if st.text_input("Password", type="password") == "yukoyuko":
                st.session_state.is_authenticated = True
                st.rerun()
        else:
            st.subheader("Add New Photo")
            with st.form("add_photo_form", clear_on_submit=True):
                new_title = st.text_input("Country / City")
                new_cat = st.selectbox("Region", ["Asia", "Africa", "North America", "South America", "Europe", "Australia"])
                new_year = st.selectbox("Year", options=[str(y) for y in range(2015, 2100)])
                uploaded_file = st.file_uploader("Select Photo", type=["jpg", "jpeg", "png"])
                new_comment = st.text_area("Short Comment")
                if st.form_submit_button("Add to Gallery"):
                    if new_title and uploaded_file:
                        st.session_state.photo_list.insert(0, {"url": Image.open(uploaded_file), "title": new_title, "year": new_year, "category": new_cat, "comment": new_comment})
                        st.session_state.show_form = False
                        st.session_state.is_authenticated = False
                        st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

# =================================================================
# 5. DISPLAY (Shows message if empty)
# =================================================================
filtered = [p for p in st.session_state.photo_list if (st.session_state.selected_cat=="ALL" or p["category"]==st.session_state.selected_cat) and (st.session_state.selected_year=="ALL" or p["year"]==st.session_state.selected_year)]
if not filtered:
    st.markdown("<p style='text-align: center; color: #8C8A87; margin-top: 100px;'>No photos yet. Click ＋ to add one!</p>", unsafe_allow_html=True)
else:
    for p in filtered:
        c2 = st.columns([1, 2, 1])[1]
        with c2:
            st.markdown(f"<div class='photo-title'>{p['title']}</div><div class='photo-meta'>{p['year']}</div>", unsafe_allow_html=True)
            st.image(p["url"], use_container_width=True)
            if p.get('comment'): st.markdown(f"<div class='photo-comment'>{p['comment']}</div>", unsafe_allow_html=True)
            st.write("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)

# =================================================================
# 6. FILTER LOGIC
# =================================================================
filtered_photos = []
for photo in st.session_state.photo_list:
    year_match = (st.session_state.selected_year == "ALL") or (photo["year"] == st.session_state.selected_year)
    cat_match = (st.session_state.selected_cat == "ALL") or (photo["category"] == st.session_state.selected_cat)
    
    if year_match and cat_match:
        filtered_photos.append(photo)

# =================================================================
# 7. PHOTO DISPLAY AREA
# =================================================================
if not filtered_photos:
    st.markdown("<p style='text-align: center; color: #8C8A87; margin-top: 100px;'>No photos found matching the criteria.</p>", unsafe_allow_html=True)
else:
    for photo in filtered_photos:
        col_left, col_main, col_right = st.columns([1, 2, 1])
        
        with col_main:
            st.markdown("<div class='single-photo-container'>", unsafe_allow_html=True)
            
            st.markdown(f"<div class='photo-title'>{photo['title']}</div>", unsafe_allow_html=True)
            st.markdown(f"<div class='photo-meta'>{photo['year']}</div>", unsafe_allow_html=True)
            
            try:
                st.image(photo["url"], use_container_width=True)
            except:
                st.error("Failed to load the image.")
            
            if photo['comment']:
                st.markdown(f"<div class='photo-comment'>{photo['comment']}</div>", unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)
            
            st.write("<div style='margin-bottom: 50px;'></div>", unsafe_allow_html=True)