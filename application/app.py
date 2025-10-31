# --- Import necessary libraries ---
import streamlit as st
import backend as sc  # Assumes your backend code is in 'backend.py'
import os


class StreamlitFrontend:
    """
    Main class for the Streamlit application.
    Manages UI state and component rendering.
    """

    # --- Text Dictionary ---
    # All display text is stored here, keyed by language.
    TEXT = {
        "en": {
            "welcome_title": "Choose your language!",
            "disclaimer_title": "⚠️ User agreement",
            "disclaimer_file": "disclaimer_en.txt",
            "accept_button": "✅ I Accept",
            "back_button": "⬅️ Back",
            "selector_title": "Choose the type of lottery!",
            "picker_title_hu5": "🎲 Pick your 5 lottery numbers",
            "picker_title_hu6": "🎲 Pick your 6 lottery numbers",
            "picker_title_hu7": "🎲 Pick your 7 lottery numbers",
            "submit_button": "Submit",
            "results_header": "🎯 Lottery Results",
            "date_col": "🗓️ Draw Date",
            "matches_col": "⭐ Matches",
            "matches_mech_col": "⭐ Matches (mechanical)",
            "matches_manual_col": "⭐ Matches (manual)",
            "success_hu5_hu6": "🎉 You won {wins} times out of {length} draws since the start of the lottery! 🎉",
            "success_hu7": "🎉 You won {wins} times out of {length} draws since the start of the lottery! 🎉",
            "last_update": "Last database update: 31/10/2025"
        },
        "hu": {
            "welcome_title": "Válaszd ki a nyelvet!",
            "disclaimer_title": "⚠️ Felhasználási feltételek",
            "disclaimer_file": "disclaimer_hu.txt",
            "accept_button": "✅ Elfogadom",
            "back_button": "⬅️ Vissza",
            "selector_title": "Válaszd ki a lottó típusát!",
            "picker_title_hu5": "🎲 Add meg az 5 nyerőszámod!",
            "picker_title_hu6": "🎲 Add meg a 6 nyerőszámod!",
            "picker_title_hu7": "🎲 Add meg a 7 nyerőszámod!",
            "submit_button": "Lássuk!",
            "results_header": "🎯 Találatok",
            "date_col": "🗓️ Húzás dátuma",
            "matches_col": "⭐ Találatok száma",
            "matches_mech_col": "⭐ Találatok száma (gépi)",
            "matches_manual_col": "⭐ Találatok száma (kézi)",
            "success_hu5_hu6": "🎉 Az eddigi {length} húzásból {wins} esetben volt találatod! 🎉",
            "success_hu7": "🎉 Az eddigi {length} húzásból {wins} esetben volt találatod! 🎉",
            "last_update": "Adatbázis utolsó frissítése: 31/10/2025"
        }
    }

    # --- Rules Dictionary ---
    # This dictionary drives the dynamic number picker page, with the lottery rules.
    LOTTERY_RULES = {
        'hu5': {
            'limit': 5,
            'max_num': 90,
            'cols': 10,
            'session_key': 'selected_numbers_hu5'
        },
        'hu6': {
            'limit': 6,
            'max_num': 45,
            'cols': 9,
            'session_key': 'selected_numbers_hu6'
        },
        'hu7': {
            'limit': 7,
            'max_num': 35,
            'cols': 7,
            'session_key': 'selected_numbers_hu7'
        }
    }

    # --- Helper Methods ---

    def _clear_session_keys(self, keys_to_clear):
        """
        A helper function to remove a list of keys from session_state.
        Used for 'Back' buttons to reset state.
        """
        for key in keys_to_clear:
            st.session_state.pop(key, None)

    # --- Page Rendering Methods ---

    def _welcome_page(self):
        """Streamlit Welcome Page for language selection."""
        st.set_page_config(page_title='Would I win the lottery?', page_icon="🎲", layout="centered")
        st.title(self.TEXT["en"]["welcome_title"])
        st.divider()

        col1, col2 = st.columns(2)
        with col1:
            if st.button("English", use_container_width=True, type="secondary"):
                st.session_state["language"] = "en"
                st.rerun()
        with col2:
            if st.button("Magyar", use_container_width=True, type="secondary"):
                st.session_state["language"] = "hu"
                st.rerun()

    def _disclaimer_page(self, txt):
        """
        Display disclaimer that must be accepted.
        """
        st.title(txt["disclaimer_title"])

        # Sanity check: Try to read the disclaimer file.
        try:
            with open(txt["disclaimer_file"], 'r', encoding='utf-8') as file:
                st.write(file.read())
        except FileNotFoundError:
            st.error(f"Error: Disclaimer file not found at '{os.path.abspath(txt['disclaimer_file'])}'.")
            # Still show buttons so user can go back.
        except Exception as e:
            st.error(f"An error occurred while reading the file: {e}")

        if st.button(txt["accept_button"], type="secondary"):
            st.session_state["disclaimer_accepted"] = True
            st.rerun()

        st.button(txt["back_button"], on_click=self._clear_session_keys, args=(['language'],))

    def _lottery_type_page(self, txt):
        """
        Display the main lottery selection buttons.
        """
        st.title(txt["selector_title"])
        st.divider()

        col1, col2, col3 = st.columns(3)

        # Highlight button if it's the currently selected lottery
        def get_button_type(lottery_id):
            if "lottery_id" not in st.session_state:
                return "secondary"
            return "primary" if st.session_state["lottery_id"] == lottery_id else "secondary"

        with col1:
            if st.button("Ötöslottó", use_container_width=True, type=get_button_type("hu5")):
                st.session_state["lottery_id"] = "hu5"
                st.rerun()

            # Back button resets the disclaimer and all lottery-related states
            back_keys = [
                "disclaimer_accepted", "lottery_id",
                "selected_numbers_hu5", "selected_numbers_hu6", "selected_numbers_hu7",
                "get_winning_numbers"
            ]
            st.button(txt["back_button"], on_click=self._clear_session_keys, args=(back_keys,))

        with col2:
            if st.button("Hatoslottó", use_container_width=True, type=get_button_type("hu6")):
                st.session_state["lottery_id"] = "hu6"
                st.rerun()

        with col3:
            if st.button("Skandináv lottó", use_container_width=True, type=get_button_type("hu7")):
                st.session_state["lottery_id"] = "hu7"
                st.rerun()

    def _number_picker_page(self, _lottery_id, txt):
        """
        A single, dynamic page for picking numbers.
        """
        st.set_page_config(page_title="Lottery Picker", layout="centered")

        # Get the rules for this lottery
        try:
            rules = self.LOTTERY_RULES[_lottery_id]
        except KeyError:
            st.error("Invalid lottery type selected. Please go back.")
            st.button(txt["back_button"], on_click=self._clear_session_keys, args=(['lottery_id'],))
            return

        limit = rules['limit']
        max_num = rules['max_num']
        num_cols = rules['cols']
        session_key = rules['session_key']

        # Use dynamic title based on lottery_id
        st.title(txt[f"picker_title_{_lottery_id}"])

        if session_key not in st.session_state:
            st.session_state[session_key] = set()

        def toggle_number(num: int):
            """Helper function to add/remove a number from the set."""
            if num in st.session_state[session_key]:
                st.session_state[session_key].remove(num)
            elif len(st.session_state[session_key]) < limit:
                st.session_state[session_key].add(num)

        # --- Draw the number grid dynamically ---
        cols = st.columns(num_cols)
        for i in range(1, max_num + 1):
            col_index = (i - 1) % num_cols
            col = cols[col_index]

            with col:
                selected = i in st.session_state[session_key]
                btn_type = "primary" if selected else "secondary"

                if st.button(str(i), key=f"num_{_lottery_id}_{i}", use_container_width=True, type=btn_type):
                    toggle_number(i)
                    st.rerun()

            # Start a new row
            if i % num_cols == 0 and i != max_num:
                cols = st.columns(num_cols)

        # --- Dynamic Submit Button ---
        is_disabled = len(st.session_state[session_key]) != limit
        if st.button(txt["submit_button"], type="primary", use_container_width=True, disabled=is_disabled):
            st.session_state.get_winning_numbers = True
            st.rerun()

    def _results_page(self, _language, _lottery_id, _user_input, txt):
        """
        Fetches and displays the results.
        """

        # --- Call Backend ---
        # Show a spinner while fetching data
        with st.spinner("Checking results..."):
            try:
                results, length = sc.WinningNumbers(_lottery_id, _user_input).check_lottery_numbers()
            except Exception as e:
                st.error(f"An error occurred while fetching results: {e}")
                st.button(txt["back_button"], on_click=self._clear_session_keys, args=(['get_winning_numbers'],))
                return

        st.header(txt["results_header"])
        st.header(txt["last_update"])

        # --- Display Results (Dynamic) ---
        if _lottery_id == "hu7":
            # 3-column layout for hu7
            col1, col2, col3 = st.columns(3)
            with col1:
                st.subheader(txt["date_col"])
            with col2:
                st.subheader(txt["matches_mech_col"])
            with col3:
                st.subheader(txt["matches_manual_col"])

            st.divider()

            for r in results:
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(r[0])  # Date
                with col2:
                    st.write(r[1])  # Match A
                with col3:
                    st.write(r[2])  # Match B

            # Complex win calculation for hu7
            wins = sum([2 if (r[1] > 0 and r[2] > 0) else 1 if (r[1] > 0 or r[2] > 0) else 0 for r in results])
            st.success(txt["success_hu7"].format(wins=wins, length=length))

        elif _lottery_id == "hu5" or _lottery_id == "hu6":
            # 2-column layout for hu5/hu6
            col1, col2 = st.columns(2)  # Use 2:1 ratio for better spacing
            with col1:
                st.subheader(txt["date_col"])
            with col2:
                st.subheader(txt["matches_col"])

            st.divider()

            for r in results:
                col1, col2 = st.columns(2)
                with col1:
                    st.write(r[0])  # Date
                with col2:
                    st.write(r[1])  # Match Count

            # Simple win calculation
            wins = len(results)
            st.success(txt["success_hu5_hu6"].format(wins=wins, length=length))

        # Back button to return to the number picker
        st.button(txt["back_button"], on_click=self._clear_session_keys, args=(['get_winning_numbers'],))

    def call_pages(self, page, language=None, txt=None, lottery_id=None, selected_numbers=None):
        """
        Calls the correct page rendering method based on the 'page' string.
        """

        if page == 'welcome':
            return self._welcome_page()

        elif page == 'disclaimer':
            return self._disclaimer_page(txt)

        elif page == 'selector':
            return self._lottery_type_page(txt)

        elif page == 'picker':
            return self._number_picker_page(lottery_id, txt)

        elif page == 'results':
            return self._results_page(language, lottery_id, selected_numbers, txt)

        else:
            raise ValueError(f"Invalid page ID: {page}")

def run_app():
    """
    Main application router.
    Uses a "guard clause" pattern to show the correct page.
    The script stops execution with 'return' after rendering each page.
    """
    frontend = StreamlitFrontend()

    # --- Page 1: Welcome / Language Selection ---
    if "language" not in st.session_state:
        frontend.call_pages('welcome')
        return

    # --- Language is set, get the correct text ---
    # Default to English if language state is somehow invalid
    txt = frontend.TEXT.get(st.session_state["language"], frontend.TEXT["en"])

    # --- Page 2: Disclaimer ---
    if not st.session_state.get("disclaimer_accepted", False):
        frontend.call_pages('disclaimer', txt=txt)
        return

    # --- Page 3: Lottery Selector ---
    if ("language" in st.session_state and
            st.session_state.get("disclaimer_accepted", True) and
            "get_winning_numbers" not in st.session_state
    ):
        frontend.call_pages('selector', txt=txt)

    # --- Page 4: Number Picker ---
    # Check this *before* the lottery selector.
    if ("language" in st.session_state and
            st.session_state.get("disclaimer_accepted", True) and
            "lottery_id" in st.session_state and
            "get_winning_numbers" not in st.session_state
    ):
        frontend.call_pages('picker', lottery_id=st.session_state["lottery_id"], txt=txt)


    # --- Page 5: Results Page ---
    if "get_winning_numbers" in st.session_state:
        lottery_id = st.session_state["lottery_id"]
        rules = frontend.LOTTERY_RULES[lottery_id]
        session_key = rules['session_key']
        selected_numbers = list(st.session_state.get(session_key, []))

        frontend.call_pages('results', st.session_state["language"], txt, lottery_id, selected_numbers)
        return


# --- Main execution ---
if __name__ == "__main__":
    run_app()
