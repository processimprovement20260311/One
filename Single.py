import streamlit as st
import random
import pandas as pd

st.set_page_config(page_title="LCT Play-by-Play Sim", page_icon="🏈", layout="wide")
st.title("🏈 LCT Live Play-by-Play Simulator")

# ============================================================
# TEAM RATINGS & WEATHER DATA
# ============================================================
RAW_RATINGS = {
    "STF": {"OFF": 91, "DEF": 99, "SPT": 91}, "BRK": {"OFF": 91, "DEF": 99, "SPT": 94}, "JRD": {"OFF": 97, "DEF": 92, "SPT": 95},
    "TAY": {"OFF": 97, "DEF": 92, "SPT": 95}, "BRE": {"OFF": 94, "DEF": 95, "SPT": 95}, "ASH": {"OFF": 96, "DEF": 94, "SPT": 91},
    "TRN": {"OFF": 93, "DEF": 94, "SPT": 94}, "RSN": {"OFF": 92, "DEF": 95, "SPT": 90}, "SZE": {"OFF": 89, "DEF": 91, "SPT": 90},
    "BRN": {"OFF": 87, "DEF": 92, "SPT": 90}, "AND": {"OFF": 86, "DEF": 91, "SPT": 81}, "ANG": {"OFF": 88, "DEF": 88, "SPT": 84},
    "HIL": {"OFF": 86, "DEF": 91, "SPT": 75}, "TOR": {"OFF": 89, "DEF": 80, "SPT": 90}, "CAS": {"OFF": 86, "DEF": 83, "SPT": 79},
    "ADR": {"OFF": 83, "DEF": 86, "SPT": 73}, "KRS": {"OFF": 78, "DEF": 89, "SPT": 80}, "OLV": {"OFF": 84, "DEF": 82, "SPT": 80},
    "GNN": {"OFF": 77, "DEF": 86, "SPT": 81}, "LXI": {"OFF": 81, "DEF": 76, "SPT": 79}, "SPH": {"OFF": 79, "DEF": 79, "SPT": 75},
    "NTL": {"OFF": 74, "DEF": 81, "SPT": 75}, "JLN": {"OFF": 82, "DEF": 69, "SPT": 82}, "RCH": {"OFF": 74, "DEF": 80, "SPT": 75},
    "HAL": {"OFF": 71, "DEF": 79, "SPT": 73}, "SRA": {"OFF": 79, "DEF": 66, "SPT": 77}, "AMB": {"OFF": 69, "DEF": 72, "SPT": 74},
    "CRT": {"OFF": 69, "DEF": 69, "SPT": 75}, "KEL": {"OFF": 72, "DEF": 66, "SPT": 76}, "KAT": {"OFF": 67, "DEF": 73, "SPT": 79},
    "RLY": {"OFF": 69, "DEF": 61, "SPT": 75}, "GRG": {"OFF": 69, "DEF": 67, "SPT": 69}
}

TEAM_OVERALLS = []
for team, stats in RAW_RATINGS.items():
    overall = round((stats["OFF"] * 3 + stats["DEF"] * 3 + stats["SPT"]) / 7, 2)
    TEAM_OVERALLS.append((team, overall))

TEAM_OVERALLS.sort(key=lambda x: x[1], reverse=True)
TEAM_DISPLAY_LIST = [f"{t} {o:.2f}" for t, o in TEAM_OVERALLS]

WEATHER_OPTIONS = ["Random", "Clear", "Extreme Rain", "Heavy Snow", "Heavy Winds", "Extreme Cold"]

# ============================================================
# GAME STATE INITIALIZATION
# ============================================================
def init_game(home_team, away_team, weather_choice):
    if weather_choice == "Random":
        r = random.random()
        actual_weather = ("Clear" if r < 0.77 else "Extreme Rain" if r < 0.82 else
                          "Heavy Snow" if r < 0.87 else "Heavy Winds" if r < 0.92 else "Extreme Cold")
    else:
        actual_weather = weather_choice

    return {
        "home": home_team, "away": away_team,
        "weather": actual_weather,
        "home_score": 0, "away_score": 0,
        "quarter": 1,
        "clock": 900,
        "possession": home_team,
        "down": 1, "distance": 10,
        "yardline": 25,
        "play_log": [],
        "stats": {
            home_team: {"Pass Yds": 0, "Rush Yds": 0, "1st Downs": 0, "Turnovers": 0},
            away_team: {"Pass Yds": 0, "Rush Yds": 0, "1st Downs": 0, "Turnovers": 0}
        },
        "game_over": False
    }

def add_log(state, text):
    state["play_log"].append(f"Q{state['quarter']} {state['clock']//60:02d}:{state['clock']%60:02d} - {text}")

# ============================================================
# PLAY ENGINE
# ============================================================
def simulate_play(state):
    if state["game_over"]: return

    off_team = state["possession"]
    def_team = state["away"] if off_team == state["home"] else state["home"]
    
    weather = state["weather"]
    pass_penalty = 0
    if weather in ["Extreme Rain", "Heavy Winds"]: pass_penalty = -3
    elif weather == "Heavy Snow": pass_penalty = -6
    elif weather == "Extreme Cold": pass_penalty = -2

    time_taken = random.randint(20, 40)
    state["clock"] -= time_taken
    if state["clock"] < 0: state["clock"] = 0

    rand = random.random()
    is_pass = False
    if state["down"] == 3 and state["distance"] >= 7: is_pass = rand < 0.85
    elif state["down"] == 2 and state["distance"] >= 5: is_pass = rand < 0.65
    else: is_pass = rand < 0.50
        
    yards_gained = 0
    is_turnover = False
    is_td = False
    is_safety = False
    play_desc = ""
    
    if is_pass:
        outcome = random.random()
        if outcome < 0.45:
            yards_gained = 0
            play_desc = "Incomplete pass."
        elif outcome < 0.50:
            yards_gained = 0
            is_turnover = True
            play_desc = f"INTERCEPTION by {def_team}!"
        elif outcome < 0.55:
            yards_gained = -random.randint(3, 8)
            play_desc = f"Sacked for a loss of {abs(yards_gained)} yards."
        else:
            yards_gained = max(1, random.randint(3, 25) + pass_penalty)
            play_desc = f"Pass complete for {yards_gained} yards."
            state["stats"][off_team]["Pass Yds"] += yards_gained
    else:
        outcome = random.random()
        if outcome < 0.05:
            yards_gained = 0
            is_turnover = True
            play_desc = f"FUMBLE! Recovered by {def_team}."
        else:
            yards_gained = random.randint(-2, 12)
            if yards_gained < 0: play_desc = f"Rush for a loss of {abs(yards_gained)} yards."
            else: play_desc = f"Rush for {yards_gained} yards."
            state["stats"][off_team]["Rush Yds"] += yards_gained

    new_yardline = state["yardline"] + yards_gained
    
    if not is_turnover:
        if new_yardline >= 100:
            is_td = True
            if off_team == state["home"]: state["home_score"] += 7
            else: state["away_score"] += 7
            play_desc += " TOUCHDOWN! Extra point is good."
            state["stats"][off_team]["1st Downs"] += 1
            state["possession"] = def_team
            state["yardline"] = 25
            state["down"] = 1
            state["distance"] = 10
        elif new_yardline <= 0:
            is_safety = True
            if def_team == state["home"]: state["home_score"] += 2
            else: state["away_score"] += 2
            play_desc += " SAFETY! 2 points."
            state["possession"] = def_team
            state["yardline"] = 40
            state["down"] = 1
            state["distance"] = 10
        else:
            state["yardline"] = new_yardline
            if yards_gained >= state["distance"]:
                state["down"] = 1
                state["distance"] = 10
                state["stats"][off_team]["1st Downs"] += 1
                play_desc += " FIRST DOWN."
            else:
                state["down"] += 1
                state["distance"] -= yards_gained
                
    if is_turnover:
        state["stats"][off_team]["Turnovers"] += 1
        state["possession"] = def_team
        state["yardline"] = 100 - state["yardline"]
        state["down"] = 1
        state["distance"] = 10
    elif state["down"] > 4:
        play_desc += " Turnover on downs."
        state["possession"] = def_team
        state["yardline"] = 100 - state["yardline"]
        state["down"] = 1
        state["distance"] = 10

    if state["down"] == 4 and not is_td and not is_turnover and not is_safety:
        punt_yards = random.randint(35, 55)
        state["possession"] = def_team
        state["yardline"] = 100 - (state["yardline"] + punt_yards)
        if state["yardline"] > 80: 
            state["yardline"] = 20
            play_desc = f"Punt for {punt_yards} yards. Touchback."
        else:
            play_desc = f"Punt for {punt_yards} yards. Fair catch."
        state["down"] = 1
        state["distance"] = 10
            
    add_log(state, play_desc)

    if state["clock"] <= 0:
        if state["quarter"] < 4:
            state["quarter"] += 1
            state["clock"] = 900
            add_log(state, f"End of Q{state['quarter']-1}. Start of Q{state['quarter']}.")
        else:
            state["game_over"] = True
            add_log(state, "End of Game.")

# ============================================================
# UI & STREAMLIT LOGIC
# ============================================================
st.subheader("Game Setup")

col1, col2, col3 = st.columns(3)

with col1:
    home_display = st.selectbox("Home Team", TEAM_DISPLAY_LIST, index=0)
    home_team = home_display.rsplit(' ', 1)[0]

with col2:
    away_display = st.selectbox("Away Team", TEAM_DISPLAY_LIST, index=1)
    away_team = away_display.rsplit(' ', 1)[0]

with col3:
    weather_choice = st.selectbox("Weather", WEATHER_OPTIONS, index=0)

st.write("")

if home_team == away_team:
    st.error("Please select two different teams.")
else:
    if st.button("Start / Reset Game", use_container_width=True, type="primary"):
        st.session_state.game = init_game(home_team, away_team, weather_choice)
        st.rerun()

    if "game" not in st.session_state or \
       st.session_state.game["home"] != home_team or \
       st.session_state.game["away"] != away_team:
        st.session_state.game = init_game(home_team, away_team, weather_choice)

    game = st.session_state.game

    st.markdown("---")
    score_cols = st.columns([1, 1, 1, 1])
    with score_cols[0]:
        st.metric(game["away"], game["away_score"])
    with score_cols[1]:
        st.metric("Quarter", f"Q{game['quarter']}")
        st.write(f"**Clock:** {game['clock']//60:02d}:{game['clock']%60:02d}")
    with score_cols[2]:
        st.metric(game["home"], game["home_score"])
    with score_cols[3]:
        st.metric("Weather", game["weather"])

    st.markdown("---")

    situation = st.empty()
    if not game["game_over"]:
        poss = game["possession"]
        yard = game["yardline"]
        if yard > 50:
            field_pos = f"{game['away']} {100-yard}"
        else:
            field_pos = f"{game['home']} {yard}"
        situation.info(f"**{poss}** has the ball at the **{field_pos}** | **{game['down']} & {game['distance']}**")
    else:
        if game["home_score"] > game["away_score"]: winner = game["home"]
        elif game["away_score"] > game["home_score"]: winner = game["away"]
        else: winner = "TIE"
        situation.success(f"**FINAL:** {winner} wins!" if winner != "TIE" else "**FINAL:** Tie Game!")

    # Updated Play Control Section
    st.write("**Simulation Controls**")
    ctrl_cols = st.columns([1, 2, 1.5, 2])
    
    with ctrl_cols[0]:
        if st.button("▶ Next Play", use_container_width=True, disabled=game["game_over"]):
            simulate_play(game); st.rerun()
            
    with ctrl_cols[1]:
        # Custom number input for plays
        custom_plays = st.number_input("Plays to Sim", min_value=1, max_value=200, value=10, label_visibility="collapsed")
        
    with ctrl_cols[2]:
        # Button to trigger the custom number
        if st.button(f"▶▶ Next {custom_plays} Plays", use_container_width=True, disabled=game["game_over"]):
            for _ in range(custom_plays):
                if not game["game_over"]: simulate_play(game)
            st.rerun()
            
    with ctrl_cols[3]:
        if st.button("⏩ Sim Rest of Game", use_container_width=True, disabled=game["game_over"]):
            while not game["game_over"]: simulate_play(game)
            st.rerun()

    st.markdown("---")

    log_col, stat_col = st.columns([2, 1])

    with stat_col:
        st.subheader("Box Score")
        box_data = []
        for stat in ["Pass Yds", "Rush Yds", "1st Downs", "Turnovers"]:
            box_data.append({
                "Stat": stat,
                game["away"]: game["stats"][game["away"]][stat],
                game["home"]: game["stats"][game["home"]][stat]
            })
        st.dataframe(pd.DataFrame(box_data), hide_index=True, use_container_width=True)

    with log_col:
        st.subheader("Play-by-Play Log")
        log_container = st.container(height=500)
        with log_container:
            for entry in reversed(game["play_log"]):
                st.text(entry)
