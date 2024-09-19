import streamlit as st
#import os
#from streamlit_navigation_bar import st_navbar
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode
from st_aggrid.shared import JsCode
from streamlit_gsheets import GSheetsConnection
import hmac


def check_password():
    """Returns `True` if the user had a correct password."""
    def login_form():
        """Form with widgets to collect user information"""
        with st.form("Credentials"):
            st.title("Consulta de :blue[Testigos] :sunglasses:")
            st.text_input("Username", key="username")
            st.text_input("Password", type="password", key="password")
            st.form_submit_button("Log in", on_click=password_entered, use_container_width=True)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in st.secrets[
            "passwords"
        ] and hmac.compare_digest(
            st.session_state["password"],
            st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the username or password.
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 User not known or password incorrect")
    return False


if not check_password():
    st.stop()


#parent_dir = os.path.dirname(os.path.abspath(__file__))
#logo_path = os.path.join(parent_dir, "mm.svg")

@st.cache_data
def load_data():
    # Create a connection object.
    conn = st.connection("gsheets", type=GSheetsConnection)
    #df = pd.read_csv("C:/Users/Miguel Sanka/Desktop/test-main/testigos_summary.csv", sep="|", encoding_errors="ignore", low_memory=False)
    df = conn.read()
    return df
#logo_path=logo_path

#page = st_navbar([""])
st.header("Consulta de testigos", divider=True)

data = load_data()

with st.form(key='my_form'):
   options = st.multiselect(
    "Ingrese el folio del contrato",
    data["Folio"].unique())
   submit_button = st.form_submit_button(label='Buscar', use_container_width=True)
   
if not(options):
   filtered = data
else:
   filtered = data[data['Folio'].isin(options)]

gb = GridOptionsBuilder.from_dataframe(filtered,
                                        editable=False)

cell_renderer =  JsCode("""
                        function(params) {return `<a href=${params.value} target="_blank">${params.value}</a>`}
                        """)

for column in data.columns:
    gb.configure_column(column, filter=True)

gb.configure_column(
    "Testigo",
    headerName="Testigo",
    cellRenderer=JsCode("""
        class UrlCellRenderer {
          init(params) {
            this.eGui = document.createElement('a');
            this.eGui.innerText = params.value;
            this.eGui.setAttribute('href', params.value);
            this.eGui.setAttribute('style', "text-decoration:none");
            this.eGui.setAttribute('target', "_blank");
          }
          getGui() {
            return this.eGui;
          }
        }
    """)
)

gb.configure_pagination(paginationPageSize=10)

grid = AgGrid(filtered,
            gridOptions=gb.build(),
            updateMode=GridUpdateMode.VALUE_CHANGED,
            allow_unsafe_jscode=True, height=800)
