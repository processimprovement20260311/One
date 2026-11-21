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
# RADIO BROADCAST PHRASE LIBRARY
# (Pronouns removed, strictly team-based)
# ============================================================
RADIO_LIBRARY = {
    "rush_short": [
        "{team} hands it off up the middle, grinding out {yards} yards.",
        "A quick dive play for {team}, the offense picks up {yards} on the ground.",
        "The offense tries to establish the run, {team} gets {yards} yards.",
        "It's a heavy dose of the run game, {team} is stopped for a short gain of {yards}.",
        "{team} keeps it on the ground, pushing the pile forward for {yards}."
    ],
    "rush_medium": [
        "{team} finds a seam! That's a solid pickup of {yards} yards.",
        "A nice cutback by {team}, the runner weaves through traffic for {yards}.",
        "Good blocking up front, {team} rumbles forward for {yards} yards.",
        "{team} lowers the shoulder and drives forward for a gain of {yards}.",
        "The ground game is working for {team}, the offense picks up {yards} on that carry."
    ],
    "rush_long": [
        "BREAKS AWAY! {team} bounces it to the outside and takes it for {yards} yards!",
        "What a run by {team}! The offense hits the second level and picks up {yards}!",
        "Huge hole! {team} explodes through it for a massive gain of {yards}.",
        "{team} turns on the jets! A spectacular {yards}-yard run!",
        "The defense couldn't bring the runner down! {team} rumbles for {yards} yards down the sideline!"
    ],
    "rush_loss": [
        "Nowhere to go! {team} is swarmed in the backfield for a loss of {yards}.",
        "The defense crashes down, stuffing {team} for a loss of {yards}.",
        "A blown-up play! {team} tries the run but loses {yards} yards.",
        "Great penetration by {def_team}! The defense drops {team} for a loss of {yards}.",
        "{team} tries to bounce it outside, but the defense is waiting. Loss of {yards}."
    ],
    "pass_short": [
        "{team} fires a quick screen, complete for {yards} yards.",
        "A dart over the middle, {team} connects for a short gain of {yards}.",
        "Quick out route, caught by {team} for {yards} yards.",
        "{team} dumps it off to the flat, picking up {yards}.",
        "High percentage throw for {team}, the offense gets {yards} on the play."
    ],
    "pass_medium": [
        "{team} drops back and finds an open man, complete for {yards} yards.",
        "A strike to the sideline! {team} picks up {yards} yards.",
        "Beautiful throw and catch for {team}, moving the chains for {yards}.",
        "The defense left the middle open, {team} takes advantage for {yards} yards.",
        "{team} threads the needle on that pass, good for {yards} yards."
    ],
    "pass_deep": [
        "{team} drops back and airs it out! Complete for {yards} yards!",
        "A deep shot by {team}, caught! That's a pickup of {yards}!",
        "The offense launches it downfield! {team} comes down with it for a huge gain of {yards}!",
        "The defense is burned! {team} connects on a beautiful deep ball for {yards} yards!",
        "BOMB! {team} goes over the top and hits paydirt for {yards} yards!"
    ],
    "pass_incomplete": [
        "Incomplete. {team} couldn't connect on that one.",
        "The pass falls incomplete, overthrown by {team}.",
        "Good coverage by {def_team}, forcing the incompletion for {team}.",
        "{team} fires it out of bounds, incomplete.",
        "Broken up! The {def_team} defense knocks the pass away from {team}."
    ],
    "sack": [
        "SACKED! {def_team} gets to the quarterback, dropping {team} for a loss of {yards}.",
        "The pocket collapses! {def_team} brings {team} down for a big loss of {yards}.",
        "Huge hit! {team} is sacked for a loss of {yards}.",
        "Nowhere to run! {def_team} wraps up {team} for a sack, a loss of {yards}.",
        "The blitz gets home! {team} goes down for a loss of {yards}."
    ],
    "turnover_int": [
        "INTERCEPTED! {def_team} takes it away! What a huge momentum swing!",
        "Picked off! The defense for {def_team} reads it perfectly and steals it from {team}.",
        "That pass is stolen! {def_team} comes down with the interception!",
        "A terrible decision by {team}! The ball is intercepted by {def_team}.",
        "TURNOVER! {def_team} jumps the route and picks off {team}!"
    ],
    "turnover_fumble": [
        "FUMBLE! The ball is loose! {def_team} recovers!",
        "The offense coughed it up! {team} loses the football, and {def_team} pounces on it!",
        "Strip sack! The defense knocks the ball out, and {def_team} recovers!",
        "Disaster for {team}! The offense puts the ball on the turf, and {def_team} takes it away.",
        "What a hit! The ball pops loose, and it's recovered by {def_team}!"
    ],
    "turnover_downs": [
        "Turnover on downs! {def_team} makes the crucial stop to take over.",
        "They go for it, but {team} is stopped short! {def_team} takes over on downs.",
        "The defense holds! {def_team} stuffs the play and forces the turnover on downs.",
        "Not enough! {team} fails to convert, and the ball goes to {def_team}.",
        "Great goal-line stand by {def_team}! {team} is denied on 4th down."
    ],
    "touchdown": [
        "TOUCHDOWN! {team} finds the end zone! The crowd goes absolutely wild!",
        "IN FOR SIX! {team} punches it across the goal line!",
        "PAYDIRT! {team} scores! That's a massive touchdown!",
        "The offense breaks the plane! {team} gets the touchdown, and the extra point is good!",
        "What a drive by {team}! It's capped off with a touchdown!"
    ],
    "field_goal_made": [
        "The kick is up... and it is GOOD! {team} puts 3 on the board.",
        "The kicker drills it right down the middle. {team} adds three points.",
        "No doubt about that one. Good from {yards} yards out for {team}.",
        "Perfect strike by the kicker! {team} gets the field goal.",
        "It just sneaks inside the upright! {team} is good for three."
    ],
    "field_goal_miss": [
        "The kick is up... and it is NO GOOD! {team} comes away empty-handed.",
        "The kicker pushes it wide right! A miss for {team}.",
        "Short! The kick doesn't have the leg, and {team} misses the field goal.",
        "It hits the upright! Unbelievable! {team} misses the kick.",
        "Wide left! {def_team} takes over after the missed field goal by {team}."
    ],
    "safety": [
        "SAFETY! {def_team} pins them in the end zone for two points!",
        "The offense is brought down in the end zone! That's a safety for {def_team}!",
        "A massive defensive play! {def_team} gets the safety.",
        "The offensive line collapses, and {team} is taken down for a safety.",
        "Two points for {def_team} as the defense traps {team} in their own end zone!"
    ],
    "punt": [
        "{team} sends the punt team out. A good boot, fair catch.",
        "The punt is away... a high spiral, fielded cleanly.",
        "{team} flips the field position with a solid punt.",
        "Rugby style punt by {team}, the coverage team gets downfield well.",
        "The punt sails out of bounds, {team} giving the defense a long field."
    ],
    "late_game_rush": [
        "They hand it off, and {team} grinds forward for {yards}. The clock is ticking!",
        "{team} keeps it on the ground, picking up {yards}. The defense is desperate to get the ball back!",
        "A crucial run by {team}! The offense picks up {yards} and keeps the chains moving.",
        "The offense is trying to bleed the clock! {team} runs for {yards}.",
        "With the game on the line, {team} goes to the ground game for {yards} yards."
    ],
    "late_game_pass": [
        "Under pressure, {team} fires it! Complete for {yards}! A massive play!",
        "The offense has to throw it, and {team} delivers a strike for {yards} yards!",
        "A clutch throw by {team} on this crucial drive, picking up {yards}!",
        "{team} drops back... steps up... and finds a window for {yards} yards!",
        "The defense knew it was coming, but {team} still completes it for {yards}!"
    ],
    "late_game_incomplete": [
        "Incomplete! The clock stops, and {team} is running out of time!",
        "Overthrown! A crucial miss for {team} in this high-pressure moment.",
        "Broken up! {def_team} makes a massive play to deny {team} the completion.",
        "The pass falls to the turf. Incomplete for {team}.",
        "The offense couldn't connect! {team} wastes a crucial down."
    ],
    "late_game_sack": [
        "MASSIVE SACK! {def_team} comes up with a huge stop, dropping {team} for a loss of {yards}!",
        "The pocket collapses! {def_team} gets the sack at the worst possible time for {team}!",
        "The offense goes down! A huge loss of {yards} for {team} as {def_team} brings the heat!",
        "SACKED! The clock keeps running, and {team} loses {yards} yards!",
        "A game-changing sack by {def_team}! {team} is pushed back {yards} yards!"
    ],
    "late_game_interception": [
        "INTERCEPTED! IT'S OVER! {def_team} seals the game with a massive pick!",
        "PICKED OFF! {def_team} comes up with the biggest play of the game, stealing it from {team}!",
        "TURNOVER! The pass is intercepted by {def_team} in the clutch!",
        "Disaster for {team}! The offense throws it right to {def_team} in a critical moment!",
        "INTERCEPTED! {def_team} jumps the route, and the sideline erupts!"
    ],
    "late_game_touchdown": [
        "TOUCHDOWN! {team} takes the lead! What an unbelievable moment!",
        "IN FOR SIX! {team} finds the end zone in the clutch! The stadium is shaking!",
        "PAYDIRT! {team} punches it in! That could be the dagger!",
        "TOUCHDOWN {team}! A legendary drive capped off with six points!",
        "The offense breaks the plane! {team} scores, and this game has been turned upside down!"
    ],
    "late_game_field_goal": [
        "THE KICK IS UP... IT IS GOOD! {team} drills it to take the lead! What a moment!",
        "Clutch kick! The kicker for {team} is ice cold, nailing the {yards}-yard field goal!",
        "It's good! {team} hits the field goal, and the pressure was immense!",
        "Right down the middle! {team} adds three crucial points!",
        "No doubt about it! The kicker for {team} splits the uprights from {yards} yards out!"
    ],
    "late_game_field_goal_miss": [
        "MISSED IT! The kick is NO GOOD, and {team} is heartbroken!",
        "WIDE RIGHT! {team} misses the crucial field goal! The defense survives!",
        "The kick is short! {def_team} takes over after a devastating miss for {team}.",
        "IT HITS THE POST! Unbelievable! {team} misses the kick in the clutch!",
        "NO GOOD! A massive sigh of relief for {def_team} as {team} fails to convert."
    ],
    "modifier_first_down": [
        " That moves the chains!",
        " And that's a first down!",
        " Enough for the first down!",
        " The offense picks up the crucial first down.",
        ""
    ]
}

# ============================================================
# GAME STATE INITIALIZATION
# ============================================================
def init_game(home_team, away_team, weather_choice, must_win=False, radio_enabled=False):
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
        "radio_enabled": radio_enabled,
    }

# ============================================================
# HELPERS
# ============================================================
def format_situation(possession, yardline, distance, home_team, away_team):
    if yardline > 50:
        opp = away_team if possession == home_team else home_team
        field_str = f"{opp} {100 - yardline}"
    else:
        field_str = f"{possession} {yardline}"
    dist_str = "Goal" if distance >= (100 - yardline) else str(distance)
    return field_str, dist_str

def kickoff(state, receiving_team):
    state["possession"] = receiving_team
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
        state["yardline"] = 25
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

def generate_radio_call(play_type, is_late_game, team, def_team, yards=0):
    key = f"late_game_{play_type}" if is_late_game and f"late_game_{play_type}" in RADIO_LIBRARY else play_type
    if key not in RADIO_LIBRARY: key = play_type
    phrase = random.choice(RADIO_LIBRARY.get(key, ["A standard play."]))
    return phrase.format(team=team, def_team=def_team, yards=abs(yards))

# ============================================================
# PLAY ENGINE
# ============================================================
def simulate_play(state):
    if state["game_over"]: return

    off_team = state["possession"]
    def_team = state["away"] if off_team == state["home"] else state["home"]
    pass_penalty = weather_pass_penalty(state["weather"])

    pre_play_down = state["down"]
    pre_play_dist = state["distance"]
    pre_play_yard = state["yardline"]
    pre_play_poss = state["possession"]
    pre_clock = state["clock"]
    pre_home_score = state["home_score"]
    pre_away_score = state["away_score"]

    # Late game definition: Q4 or OT, score within 8 points, AND under 8 minutes (480s)
    is_late_game = (state["quarter"] >= 4 and abs(state["home_score"] - state["away_score"]) <= 8 and state["clock"] <= 480)

    # --- 1. 4th Down Decision ---
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
            if state["yardline"] >= 62: is_fg = True
            else: is_punt = True

    # --- 2. Simulate Play ---
    yards_gained = 0
    is_turnover = False
    is_int = False
    is_td = False
    is_safety = False
    is_incomplete = False
    play_desc = ""
    radio_type = ""

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
            radio_type = "field_goal_made" if not is_late_game else "late_game_field_goal"
        else:
            play_desc = f"{fg_dist}-yard field goal is NO GOOD."
            state["possession"] = def_team
            spot_of_kick = state["yardline"] - 7
            state["yardline"] = max(20, 100 - spot_of_kick)
            state["down"] = 1
            state["distance"] = 10
            radio_type = "field_goal_miss" if not is_late_game else "late_game_field_goal_miss"
            
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
                final_yard = min(99, catch_yard + ret_yards)
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
        radio_type = "punt"
        
    else:
        # Standard offensive play
        if state["yardline"] >= 80: is_pass = random.random() < 0.35
        elif state["down"] == 3 and state["distance"] >= 7: is_pass = random.random() < 0.85
        elif state["down"] == 2 and state["distance"] >= 5: is_pass = random.random() < 0.65
        else: is_pass = random.random() < 0.50

        if is_pass:
            outcome = random.random()
            if outcome < 0.35:
                yards_gained = 0
                is_incomplete = True
                play_desc = "Incomplete pass."
                radio_type = "pass_incomplete" if not is_late_game else "late_game_incomplete"
            elif outcome < 0.375:
                yards_gained = 0
                is_turnover = True
                is_int = True
                play_desc = f"INTERCEPTION by {def_team}!"
                radio_type = "turnover_int" if not is_late_game else "late_game_interception"
            elif outcome < 0.44:
                sack_loss = random.randint(3, 7)
                if state["yardline"] - sack_loss <= 2: sack_loss = max(0, state["yardline"] - 2)
                yards_gained = -sack_loss
                play_desc = f"Sacked for a loss of {sack_loss} yards." if sack_loss > 0 else "Sack blown dead at the line."
                radio_type = "sack" if not is_late_game else "late_game_sack"
            else:
                yards_gained = max(1, random.randint(3, 25) + pass_penalty)
                play_desc = f"Pass complete for {yards_gained} yards."
                state["stats"][off_team]["Pass Yds"] += yards_gained
                if yards_gained >= 20: radio_type = "pass_deep" if not is_late_game else "late_game_pass"
                elif yards_gained >= 8: radio_type = "pass_medium" if not is_late_game else "late_game_pass"
                else: radio_type = "pass_short" if not is_late_game else "late_game_pass"
        else:
            outcome = random.random()
            if outcome < 0.005:
                yards_gained = 0
                is_turnover = True
                play_desc = f"FUMBLE! Recovered by {def_team}."
                radio_type = "turnover_fumble"
            else:
                yards_gained = random.randint(-2, 12)
                if yards_gained < 0:
                    play_desc = f"Rush for a loss of {abs(yards_gained)} yards."
                    radio_type = "rush_loss" if not is_late_game else "late_game_rush"
                else:
                    play_desc = f"Rush for {yards_gained} yards."
                    state["stats"][off_team]["Rush Yds"] += yards_gained
                    if yards_gained >= 15: radio_type = "rush_long" if not is_late_game else "late_game_rush"
                    elif yards_gained >= 5: radio_type = "rush_medium" if not is_late_game else "late_game_rush"
                    else: radio_type = "rush_short" if not is_late_game else "late_game_rush"

        if not is_turnover and (state["yardline"] + yards_gained) <= 0:
            if random.random() < 0.85:
                yards_gained = max(0, 1 - state["yardline"])
                play_desc += " (Stopped short of the goal line.)"

        new_yardline = state["yardline"] + yards_gained

        if not is_turnover:
            if new_yardline >= 100:
                is_td = True
                if off_team == state["home"]: state["home_score"] += 7
                else: state["away_score"] += 7
                play_desc += " TOUCHDOWN! Extra point is good. "
                state["stats"][off_team]["1st Downs"] += 1
                ret = kickoff(state, def_team)
                play_desc += ret
                radio_type = "touchdown" if not is_late_game else "late_game_touchdown"
            elif new_yardline <= 0:
                is_safety = True
                if def_team == state["home"]: state["home_score"] += 2
                else: state["away_score"] += 2
                play_desc += " SAFETY! 2 points."
                state["possession"] = def_team
                state["yardline"] = 40
                state["down"] = 1
                state["distance"] = 10
                radio_type = "safety"
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
                    state["possession"] = def_team
                    state["yardline"] = 20 if spot >= 100 else 100 - spot
                    state["down"] = 1
                    state["distance"] = 10
            else:
                state["possession"] = def_team
                state["yardline"] = max(1, 100 - state["yardline"])
                state["down"] = 1
                state["distance"] = 10
        elif state["down"] > 4:
            play_desc += " Turnover on downs."
            state["possession"] = def_team
            state["yardline"] = max(1, 100 - state["yardline"])
            state["down"] = 1
            state["distance"] = 10
            radio_type = "turnover_downs"

    # --- 3. Log the play using the PRE-PLAY situation ---
    q = state["quarter"]
    q_label = f"OT{ q - 4 }" if q > 4 else f"Q{q}"
    clock_str = f"{pre_clock//60:02d}:{pre_clock%60:02d}"
    field_str, down_str = format_situation(pre_play_poss, pre_play_yard, pre_play_dist, state["home"], state["away"])
    
    log_entry = f"{q_label} {clock_str} | {pre_play_poss} ({pre_play_down} & {down_str} at {field_str}) - {play_desc}"

    # Build Game Time Context for Radio Call
    if state.get("radio_enabled"):
        # Determine score context
        if pre_home_score == pre_away_score:
            score_ctx = "game tied"
        else:
            leader = state["home"] if pre_home_score > pre_away_score else state["away"]
            trailer = state["away"] if leader == state["home"] else state["home"]
            margin = abs(pre_home_score - pre_away_score)
            score_ctx = f"{leader} leading by {margin}" if off_team == leader else f"{trailer} trailing by {margin}"

        # Time context
        if state["quarter"] == 4:
            time_ctx = f"{clock_str} remaining in the 4th"
        elif state["quarter"] > 4:
            time_ctx = f"{clock_str} remaining in OT"
        elif state["quarter"] == 1:
            time_ctx = f"{clock_str} remaining in the 1st"
        elif state["quarter"] == 2:
            time_ctx = f"{clock_str} remaining in the 2nd"
        else:
            time_ctx = f"{clock_str} remaining in the 3rd"

        setup_line = f"{pre_play_down} & {down_str} with {time_ctx}. {score_ctx}."
        
        # Build the action
        radio_text = generate_radio_call(radio_type, is_late_game, off_team, def_team, yards_gained)
        if "FIRST DOWN" in play_desc and "modifier_first_down" in RADIO_LIBRARY:
            radio_text += random.choice(RADIO_LIBRARY["modifier_first_down"])

        log_entry += f"\n\n🎙️ *\"{setup_line} {radio_text}\"*"

    state["play_log"].append(log_entry)

    # --- 4. Clock Management ---
    if is_incomplete or is_fg or is_punt: time_taken = random.randint(5, 10)
    elif is_td or is_safety: time_taken = random.randint(5, 15)
    elif state["down"] in (1, 2) and random.random() < 0.3: time_taken = random.randint(10, 20)
    else: time_taken = random.randint(25, 40)
    
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

col1, col2, col3 = st.columns(3)

with col1:
    home_display = st.selectbox("Home Team", TEAM_DISPLAY_LIST, index=0)
    home_team = home_display.rsplit(' ', 1)[0]

with col2:
    away_display = st.selectbox("Away Team", TEAM_DISPLAY_LIST, index=1)
    away_team = away_display.rsplit(' ', 1)[0]

with col3:
    weather_choice = st.selectbox("Weather", WEATHER_OPTIONS, index=0)

col4, col5 = st.columns(2)
with col4:
    must_win = st.checkbox("Must produce a winner (OT)", value=False)
with col5:
    radio_enabled = st.checkbox("🎙️ Enable Radio Broadcast", value=False)

st.write("")

if home_team == away_team:
    st.error("Please select two different teams.")
else:
    if st.button("Start / Reset Game", use_container_width=True, type="primary"):
        st.session_state.game = init_game(home_team, away_team, weather_choice, must_win=must_win, radio_enabled=radio_enabled)
        st.rerun()

    if "game" not in st.session_state or \
       st.session_state.game["home"] != home_team or \
       st.session_state.game["away"] != away_team:
        st.session_state.game = init_game(home_team, away_team, weather_choice, must_win=must_win, radio_enabled=radio_enabled)

    st.session_state.game["radio_enabled"] = radio_enabled
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
        log_container = st.container(height=600)
        with log_container:
            for entry in reversed(game["play_log"]):
                st.markdown(entry)
