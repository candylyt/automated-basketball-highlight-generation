#TODO: Review changes needed with this class -> single side only

class ScoreCounter(object):
    #Handles simple score and shooting counting
    def __init__(self, quarters):
        self.makes = [0] * max(1, len(quarters))
        self.attempts = [0] * max(1, len(quarters))

        self.quarters = quarters
        self.current_quarter = 0


    def set_quarter(self, timestamp):
        if len(self.quarters) > 0 and self.current_quarter < len(self.quarters):
            # Assuming all time stamps are formatted to hh:mm:ss, we can do direct string comparison
            if timestamp > self.quarters[self.current_quarter]:
                self.current_quarter += 1
        
    def make(self, timestamp, side):
        self.set_quarter(timestamp)
        self.makes[self.current_quarter-1] += 1
        self.attempts[self.current_quarter-1] += 1
        return None

    def attempt(self, timestamp, side):
        self.set_quarter(timestamp)
        self.attempts[self.current_quarter-1] += 1
        return None

    def report(self):
        return {
            'makes' : self.makes,
            'attempts' : self.attempts
        }
        


class MatchScoreCounter(ScoreCounter):
    #Handles match score and shooting counting with possible side switching
    def __init__(self, quarters, is_switched, switch_time):
        super().__init__(quarters)
        self.team_A_attempts = [0]
        self.team_B_attempts = [0]
        self.team_A_makes = [0]
        self.team_B_makes = [0]

        self.switch_time = switch_time if is_switched else '99:99:99'
        self.has_switched = False

    def attempt(self, timestamp, side) -> str:
        self.set_quarter(timestamp)
        
        if (not self.has_switched) and (timestamp > self.switch_time):
            self.has_switched = True
        
        if (side == 1 and not self.has_switched) or (side == 2 and self.has_switched):
            self.team_A_attempts[self.current_quarter-1] += 1
            return 'A'
        else:
            self.team_B_attempts[self.current_quarter-1] += 1
            return 'B'

    def make(self, timestamp, side) -> str: 
        self.set_quarter(timestamp)
        
        if (not self.has_switched) and (timestamp > self.switch_time):
            self.has_switched = True
            print("Side switched")
        
        if (side == 1 and not self.has_switched) or (side == 2 and self.has_switched):
            self.team_A_attempts[self.current_quarter-1] += 1
            self.team_A_makes[self.current_quarter-1] += 1
            return 'A'
        else:
            self.team_B_attempts[self.current_quarter-1] += 1
            self.team_B_makes[self.current_quarter-1] += 1
            return 'B'

    def report(self):
        return {
            "team_A_attempts": self.team_A_attempts,
            "team_A_makes": self.team_A_makes,
            "team_B_attempts": self.team_B_attempts,
            "team_B_makes": self.team_B_makes,
        }