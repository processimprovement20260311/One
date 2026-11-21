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
def init_game(home_team, away_team, weather_choice, must_win=False):
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
            home_team: {"Pass Yds": 0, "Rush Yds": 0, "1st Downs": 0, "Turnovers": 0,
                        "FG Made": 0, "FG Att": 0, "Return Yds": 0, "Return TDs": 0},
            away_team: {"Pass Yds": 0, "Rush Yds": 0, "1st Downs": 0, "Turnovers": 0,
                        "FG Made": 0, "FG Att": 0, "Return Yds": 0, "Return TDs": 0}
        },
        "game_over": False,
        "must_win": must_win,
        "overtime": False,
    }

# ============================================================
# HELPERS
# ============================================================
def format_situation(possession, yardline, distance, home_team, away_team):
    """Formats the field position and down & distance correctly."""
    if yardline > 50:
        opp = away_team if possession == home_team else home_team
        field_str = f"{opp} {100 - yardline}"
    else:
        field_str = f"{possession} {yardline}"
        
    dist_str = "Goal" if distance >= (100 - yardline) else str(distance)
    return field_str, dist_str

def kickoff(state, receiving_team):
    """Simulate a kickoff and return."""
    state["possession"] = receiving_team
    
    # 60% touchback, 38% return, 2% return TD
    r = random.random()
    if r < 0.60:
        state["yardline"] = 25
        ret_desc = "Touchback."
    elif r < 0.98:
        ret_yards = random.randint(15, 35)
        state["yardline"] = ret_yards
        state["stats"][receiving_team]["Return Yds"] += ret_yards
        ret_desc = f"Returned {ret_yards} yards to the {receiving_team} {ret_yards}."
    else:
        state["yardline"] = 25 # Reset for PAT
        state["stats"][receiving_team]["Return TDs"] += 1
        if receiving_team == state["home"]: state["home_score"] += 7
        else: state["away_score"] += 7
        ret_desc = "TOUCHDOWN ON THE RETURN!"
        
    state["down"] = 1
    state["distance"] = 10
    return ret_desc

def weather_pass_penalty(weather):
    if weather in ["Extreme Rain", "Heavy Winds"]: return -3
    if weather == "Heavy Snow": return -6
    if weather == "Extreme Cold": return -2
    return 0

# ============================================================
# PLAY ENGINE
# ============================================================
def simulate_play(state):
    if state["game_over"]: return

    off_team = state["possession"]
    def_team = state["away"] if off_team == state["home"] else state["home"]
    pass_penalty = weather_pass_penalty(state["weather"])

    # Capture pre-play snapshot for the log
    pre_play_down = state["down"]
    pre_play_dist = state["distance"]
    pre_play_yard = state["yardline"]
    pre_play_poss = state["possession"]

    # --- 1. 4th Down Decision (Evaluated BEFORE the play starts) ---
    is_fg = False
    is_punt = False
    
    if state["down"] == 4:
        trailing = (
            (off_team == state["home"] and state["home_score"] < state["away_score"]) or
            (off_team == state["away"] and state["away_score"] < state["home_score"])
        )
        go_for_it = (
            (state["distance"] <= 2 and state["yardline"] >= 60) or
            (state["quarter"] >= 4 and state["clock"] < 300 and trailing)
        )

        if not go_for_it:
            if state["yardline"] >= 62:
                is_fg = True
            else:
                is_punt = True

    # --- 2. Simulate the actual play ---
    yards_gained = 0
    is_turnover = False
    is_int = False
    is_td = False
    is_safety = False
    is_incomplete = False
    play_desc = ""

    if is_fg:
        fg_dist = (100 - state["yardline"]) + 17
        make_prob = max(0.0, min(0.98, 0.95 - (fg_dist - 20) * 0.014))
        state["stats"][off_team]["FG Att"] += 1
        if random.random() < make_prob:
            if off_team == state["home"]: state["home_score"] += 3
            else: state["away_score"] += 3
            state["stats"][off_team]["FG Made"] += 1
            play_desc = f"{fg_dist}-yard field goal is GOOD. "
            ret = kickoff(state, def_team)
            play_desc += ret
        else:
            play_desc = f"{fg_dist}-yard field goal is NO GOOD."
            state["possession"] = def_team
            spot_of_kick_from_offense = state["yardline"] - 7
            new_yardline_from_def = 100 - spot_of_kick_from_offense
            state["yardline"] = max(20, new_yardline_from_def)
            state["down"] = 1
            state["distance"] = 10
    elif is_punt:
        punt_yards = random.randint(35, 55)
        landing = state["yardline"] + punt_yards
        state["possession"] = def_team
        
        if landing >= 100:
            state["yardline"] = 20
            play_desc = f"Punt for {punt_yards} yards. Touchback."
        else:
            catch_yard = 100 - landing
            r = random.random()
            if r < 0.25:
                state["yardline"] = catch_yard
                play_desc = f"Punt for {punt_yards} yards. Fair catch at the {catch_yard}."
            elif r < 0.97:
                ret_yards = random.randint(2, 15)
                final_yard = catch_yard + ret_yards
                if final_yard >= 100: final_yard = 99
                state["yardline"] = final_yard
                state["stats"][def_team]["Return Yds"] += ret_yards
                play_desc = f"Punt for {punt_yards} yards. Returned {ret_yards} yards to the {final_yard}."
            else:
                state["yardline"] = 25
                state["stats"][def_team]["Return TDs"] += 1
                if def_team == state["home"]: state["home_score"] += 7
                else: state["away_score"] += 7
                play_desc = f"Punt for {punt_yards} yards. RETURNED FOR A TOUCHDOWN!"
                ret = kickoff(state, off_team)
                play_desc += " " + ret

        state["down"] = 1
        state["distance"] = 10
    else:
        # Standard offensive play
        if state["yardline"] >= 80:
            is_pass = random.random() < 0.35
        elif state["down"] == 3 and state["distance"] >= 7:
            is_pass = random.random() < 0.85
        elif state["down"] == 2 and state["distance"] >= 5:
            is_pass = random.random() < 0.65
        else:
            is_pass = random.random() < 0.50

        if is_pass:
            outcome = random.random()
            if outcome < 0.35:
                yards_gained = 0
                is_incomplete = True
                play_desc = "Incomplete pass."
            elif outcome < 0.375:
                yards_gained = 0
                is_turnover = True
                is_int = True
                play_desc = f"INTERCEPTION by {def_team}!"
            elif outcome < 0.44:
                sack_loss = random.randint(3, 7)
                if state["yardline"] - sack_loss <= 2:
                    sack_loss = max(0, state["yardline"] - 2)
                yards_gained = -sack_loss
                play_desc = (f"Sacked for a loss of {sack_loss} yards." if sack_loss > 0
                             else "Sack blown dead at the line.")
            else:
                yards_gained = max(1, random.randint(3, 25) + pass_penalty)
                play_desc = f"Pass complete for {yards_gained} yards."
                state["stats"][off_team]["Pass Yds"] += yards_gained
        else:
            outcome = random.random()
            if outcome < 0.005:
                yards_gained = 0
                is_turnover = True
                play_desc = f"FUMBLE! Recovered by {def_team}."
            else:
                yards_gained = random.randint(-2, 12)
                if yards_gained < 0:
                    play_desc = f"Rush for a loss of {abs(yards_gained)} yards."
                else:
                    play_desc = f"Rush for {yards_gained} yards."
                state["stats"][off_team]["Rush Yds"] += yards_gained

        # Safety valve
        if not is_turnover and (state["yardline"] + yards_gained) <= 0:
            if random.random() < 0.85:
                yards_gained = max(0, 1 - state["yardline"])
                play_desc += " (Stopped short of the goal line.)"

        new_yardline = state["yardline"] + yards_gained

        # Apply Result
        if not is_turnover:
            if new_yardline >= 100:
                is_td = True
                if off_team == state["home"]: state["home_score"] += 7
                else: state["away_score"] += 7
                play_desc += " TOUCHDOWN! Extra point is good. "
                state["stats"][off_team]["1st Downs"] += 1
                ret = kickoff(state, def_team)
                play_desc += ret
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

        # Turnovers
        if is_turnover:
            state["stats"][off_team]["Turnovers"] += 1
            if is_int:
                if random.random() < 0.12:
                    if def_team == state["home"]: state["home_score"] += 7
                    else: state["away_score"] += 7
                    play_desc += " Returned for a TOUCHDOWN! "
                    ret = kickoff(state, off_team)
                    play_desc += ret
                else:
                    ret = random.randint(0, 20)
                    spot = state["yardline"] + ret
                    if spot >= 100:
                        state["possession"] = def_team
                        state["yardline"] = 20
                    else:
                        state["possession"] = def_team
                        state["yardline"] = 100 - spot
                    state["down"] = 1
                    state["distance"] = 10
            else:
                state["possession"] = def_team
                state["yardline"] = 100 - state["yardline"]
                if state["yardline"] < 1: state["yardline"] = 1
                state["down"] = 1
                state["distance"] = 10
        elif state["down"] > 4:
            play_desc += " Turnover on downs."
            state["possession"] = def_team
            state["yardline"] = 100 - state["yardline"]
            if state["yardline"] < 1: state["yardline"] = 1
            state["down"] = 1
            state["distance"] = 10

    # --- 3. Log the play using the PRE-PLAY situation ---
    q = state["quarter"]
    q_label = f"OT{ q - 4 }" if q > 4 else f"Q{q}"
    clock_str = f"{state['clock']//60:02d}:{state['clock']%60:02d}"
    
    field_str, down_str = format_situation(pre_play_poss, pre_play_yard, pre_play_dist, state["home"], state["away"])
    
    log_entry = f"{q_label} {clock_str} | {pre_play_poss} ({pre_play_down} & {down_str} at {field_str}) - {play_desc}"
    state["play_log"].append(log_entry)

    # --- 4. Clock Management ---
    if is_incomplete or is_fg or is_punt:
        time_taken = random.randint(5, 10)
    elif is_td or is_safety:
        time_taken = random.randint(5, 15)
    elif state["down"] in (1, 2) and random.random() < 0.3:
        time_taken = random.randint(10, 20)
    else:
        time_taken = random.randint(25, 40)
    
    state["clock"] -= time_taken
    if state["clock"] < 0: state["clock"] = 0

    # --- 5. End of Quarter / OT Logic ---
    if state["clock"] <= 0:
        if state["quarter"] < 4:
            state["quarter"] += 1
            state["clock"] = 900
            state["play_log"].append(f"--- End of Q{state['quarter']-1}. Start of Q{state['quarter']}. ---")
        elif (state["home_score"] == state["away_score"] and state["must_win"] and not state["overtime"]):
            state["overtime"] = True
            state["quarter"] = 5
            state["clock"] = 600
            state["play_log"].append("--- End of regulation. Overtime! ---")
        elif state["overtime"] and state["home_score"] == state["away_score"]:
            state["clock"] = 600
            state["play_log"].append("--- End of OT period. Another OT period! ---")
        else:
            state["game_over"] = True
            state["play_log"].append("--- End of Game. ---")

    if state["overtime"] and not state["game_over"]:
        if (is_td or is_safety or is_fg):
            state["game_over"] = True
            state["play_log"].append("--- Overtime score — Game Over. ---")

# ============================================================
# UI & STREAMLIT LOGIC
# ============================================================
st.subheader("Game Setup")

col1, col2, col3, col4 = st.columns(4)

with col1:
    home_display = st.selectbox("Home Team", TEAM_DISPLAY_LIST, index=0)
    home_team = home_display.rsplit(' ', 1)[0]

with col2:
    away_display = st.selectbox("Away Team", TEAM_DISPLAY_LIST, index=1)
    away_team = away_display.rsplit(' ', 1)[0]

with col3:
    weather_choice = st.selectbox("Weather", WEATHER_OPTIONS, index=0)

with col4:
    must_win = st.checkbox("Must produce a winner (OT)", value=False)

st.write("")

if home_team == away_team:
    st.error("Please select two different teams.")
else:
    if st.button("Start / Reset Game", use_container_width=True, type="primary"):
        st.session_state.game = init_game(home_team, away_team, weather_choice, must_win=must_win)
        st.rerun()

    if "game" not in st.session_state or \
       st.session_state.game["home"] != home_team or \
       st.session_state.game["away"] != away_team:
        st.session_state.game = init_game(home_team, away_team, weather_choice, must_win=must_win)

    game = st.session_state.game

    st.markdown("---")
    score_cols = st.columns([1, 1, 1, 1])
    with score_cols[0]:
        st.metric(game["away"], game["away_score"])
    with score_cols[1]:
        q_label = f"OT{game['quarter'] - 4}" if game["quarter"] > 4 else f"Q{game['quarter']}"
        st.metric("Quarter", q_label)
        st.write(f"**Clock:** {game['clock']//60:02d}:{game['clock']%60:02d}")
    with score_cols[2]:
        st.metric(game["home"], game["home_score"])
    with score_cols[3]:
        st.metric("Weather", game["weather"])

    st.markdown("---")

    situation = st.empty()
    if not game["game_over"]:
        field_str, dist_str = format_situation(game["possession"], game["yardline"], game["distance"], game["home"], game["away"])
        situation.info(f"**{game['possession']}** has the ball at the **{field_str}** | **{game['down']} & {dist_str}**")
    else:
        if game["home_score"] > game["away_score"]: winner = game["home"]
        elif game["away_score"] > game["home_score"]: winner = game["away"]
        else: winner = "TIE"
        situation.success(f"**FINAL:** {winner} wins!" if winner != "TIE" else "**FINAL:** Tie Game!")

    st.write("**Simulation Controls**")
    ctrl_cols = st.columns([1, 2, 1.5, 2])

    with ctrl_cols[0]:
        if st.button("▶ Next Play", use_container_width=True, disabled=game["game_over"]):
            simulate_play(game); st.rerun()

    with ctrl_cols[1]:
        custom_plays = st.number_input("Plays to Sim", min_value=1, max_value=200, value=10, label_visibility="collapsed")

    with ctrl_cols[2]:
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
        for stat in ["Pass Yds", "Rush Yds", "1st Downs", "Turnovers", "FG Made", "FG Att", "Return Yds", "Return TDs"]:
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
