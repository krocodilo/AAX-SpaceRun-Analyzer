from utils import folder_name
from os import path, listdir


#########################################################
###  OPTIONS
##
worstCaseScenario = False    # Execute assuming the lowest crash multipliers come first
profitOnAllDays = True     # All days must be profitable

findMiminumBalance = True   # Find the minimum initial balance required
initialbalance = 50     # initial account balance (monetary units). Ignored if findMiminumBalance = True
balStep = 5         # Step with which to calculate the minimum balance for profit. Ignored if findMiminumBalance = False
maxInitBalance = 1000    # Maximum initial balance. Ignored if findMiminumBalance = False

bet = 1           # Amount to bet in each match. Must be between 1 and 300
precision = 0.1         # Precision for the generated multipliers (steps between each)
minimumCommonMults = 2  # Minimum of common profitable multipliers between all days
maxMultsToShow = 2      # Maximum number of profitable multipliers to show for each file
maxCommonMultsToShow = minimumCommonMults   # Maximum profitable common multipliers to show at the end
#
#########################################################


def validate_and_print_option():
    # Print options used and check for basic errors
    p = [["worstCaseScenario:", worstCaseScenario, "Execute assuming the lowest crash multipliers come first."],
        ["profitOnAllDays:", profitOnAllDays, "All days must be profitable."],
        ["findMiminumBalance:", findMiminumBalance, "Find the minimum initial balance required."]]
    if findMiminumBalance:
        p.extend([ ["balStep:", str(balStep)+"$", "Step with which to calculate the minimum balance for profit."],
            ["maxInitBalance:", str(maxInitBalance)+"$", "Maximum initial balance allowed."] ])
    else:
        p.append( ["initialbalance:", str(initialbalance)+"$", "Initial account balance (monetary units)." ] )
    p.extend([
        ["bet:", str(bet)+"$", "Amount to bet in each match. Must be between 1 and 300."],
        ["precision:", precision, "Precision for the generated multipliers (steps between each)."],
        ["minimumCommonMults:", minimumCommonMults, "Minimum of common profitable multipliers between all days."],
        ["maxMultsToShow:", maxMultsToShow, "Maximum number of profitable multipliers to show for each file."],
        ["maxCommonMultsToShow:", maxCommonMultsToShow, "Maximum profitable common multipliers to show at the end.\n"] ])

    for l in p:  print( str(l[0]).ljust(22), (str(l[1])+"\t").expandtabs(max(8, len(str(maxInitBalance))+2)) + l[2] )

    # Quick validations
    if initialbalance <= 0:     raise Exception("\nERROR: 'initialbalance' must be above 0.")
    if balStep <= 0:    raise Exception("\nERROR: 'balStep' must be above 0.")
    if maxInitBalance < balStep:    raise Exception("\nERROR: 'maxInitBalance' must be greater than 'balStep'.")    # Can be equal
    if bet < 1 or bet > 300:    raise Exception("\nERROR: 'bet' must be above or equal to 1, or bellow or equal to 300.")
    if not findMiminumBalance and bet > initialbalance:     raise Exception("\nERROR: 'bet' amount must not exceed the 'initialbalance'.")
    if precision <= 0.0:    raise Exception("\nERROR: 'precision' must be above 0.0")
    if minimumCommonMults < 1 or maxMultsToShow < 1 or maxCommonMultsToShow < 1:
        raise Exception("\nERROR: please check the options values.")

##############################

def get_files_list():

    dir = path.join(folder_name)

    if not path.isdir(dir):
        raise Exception("Directory", dir, "does not exist!")
        
    files = []
    for filename in listdir(dir):
        if filename.endswith(".csv"):
            files.append(path.join(folder_name, filename))
    return files

##############################

def read_file(filepath):
    # Read the file and do some quick analysis

    dict = {}
    dict['mults'] = []      # will save the list of all crash multipliers
    # dict['sum'] = 0.0           # summation of all, in order to calculate the average
    # dict['totalnums'] = 0       # total number of multipliers collected
    # dict['min'] = 100000.0
    dict['max'] = 0.0
    # dict['appear'] = {}       # will save the number of each multiplier, rounded down to 1 decimal

    firstline = True
    with open(filepath, "r") as file:
        for line in file:
            if firstline:
                firstline = False
                continue     # ignore the first line (CSV header)

            tmp = line.strip().split(',')

            try:
                if len(tmp) != 2: raise Exception
                m = float( tmp[1] )
            except Exception:
                print("\n-> Format Error in file '" + filepath + "', in line:", line)
                continue
                
            dict['mults'].append( m )
            # if m < dict['min']: dict['min'] = m
            if m > dict['max']: dict['max'] = m

            # dict['totalnums'] = dict['totalnums'] + 1
            # dict['sum'] = dict['sum'] + m
            # mr = round(m, 1)        # round down to 1 decimal
            # dict['appear'][mr] = dict['appear'].get(mr, 0) + 1

    return dict

##############################

def show_profits(profits, commonMults, inibalance=None):
    # Print the data on the console
    print()

    if findMiminumBalance:
        # If all days have profit
        print("\n////////////////////////////////////////////////////////////\n" +
        "Balance:", round(inibalance), "$\t///////////////////////////////////////////")
    
    for day in profits:
        # Show all profitable multipliers (unordered) for each file that has profits
        print("\nTarget multipliers with profit (" + day + "):")

        numShown = 0
        for mult in profits[day]:
            print("> ", str(mult) + "x  - ", profits[day][mult],"$")
            numShown = numShown + 1
            if numShown == maxMultsToShow:
                if numShown < len(profits[day]):  print("...")
                break


    if commonMults is None or len(commonMults) == 0:
        print("\n\n-> There are no profitable multipliers common to all days...\n")
        return

    print("\n\n__________________________________________\n_________________________________________/\n"
        "Target Multipliers Common to All Days:\n\n"+
        "Multiplier\tMin: \tMax: \tAvg: \t\tTotal for all days:".expandtabs(10))
    numShown = 0
    for m in sorted(commonMults):
        min = 10000000
        max = 0
        sum = 0

        for day in profits:
            prof = profits[day][m]   # the profit of thet target multiplier on that day
            if prof > max:  max = prof
            if prof < min:  min = prof
            sum = sum + prof

        print((
            str(m) + "x\t->\t" + str(min) + " $\t" + str(max) + " $\t" +
            str(round(sum / len(profits))) + " $\t\t" + str(sum) + " $"
            ).expandtabs(10))

        numShown = numShown + 1
        if numShown == maxCommonMultsToShow:
            if numShown < len(commonMults):  print("...")
            break
        
##############################

def calc_daily_profit(multipliers, highestMult, initbalance):
    # Calculate profits for each multiplier (on the specific day)

    tmult = 1.0 + precision     # starting target multiplier (its the minimum possible)
    profit = {}     # target multiplier : profit

    if worstCaseScenario:
        multiplierHistory = sorted(multipliers)
    else:
        multiplierHistory = multipliers

    while tmult < highestMult:
        balance = initbalance

        for crashmult in multiplierHistory:
            balance = balance - bet     # execute the bet

            if tmult < crashmult:
                # player only wins if the target multiplier is below the crash multiplier
                balance = balance + (bet * tmult)
            # else:
                # if target mult is above or equal to the crash multiplier (unreasheable),
                # the player looses the betting amount

            if balance < bet:
                # If there's no more money to bet
                balance = 0
                break

        profit[round(tmult, 2)] = round(balance)
        tmult = tmult + precision

    return profit

##############################

def calc_profits(days, initbalance):
    # Calculate profitable target multipliers for all days
    profits = {}
    commonMults = None

    for day in days:
        res = calc_daily_profit( days.get(day)['mults'], days.get(day)['max'], initbalance )
        p = {}  # holds all profitable multipliers and their respective profit

        for tmult in res:
            balance = res[tmult]
            if balance > 0:     # if profit
                p[tmult] = balance

        if len(p) > 0:
            # If there is profit with this file/day
            profits[day] = p
            if commonMults is None:
                commonMults = set( p )
            else:
                # Calculate all common profitable multipliers between this and the previous day(s)
                commonMults.intersection_update( p )

            if profitOnAllDays and len(commonMults) == 0:  return None, None
                # If there are no common profitable multipliers between all days

            if len(commonMults) < minimumCommonMults:  return None, None
        

    if len(profits) == 0:  return None, None

    if profitOnAllDays is True and len(profits) != len(days):  return None, None
        # If not all days have profit, and that is required

    return profits, commonMults


##############################

def start():
    dayfiles = get_files_list()

    days = {}
    for filepath in dayfiles:
        # parse information from all CSV files in the directory
        try:
            dict = read_file(filepath)
            days[path.basename(filepath)] = dict

        except Exception:
            print("\n-> ERROR reading the file", filepath)

    profits = {}
    commonMults = set()
    if findMiminumBalance:
        # Calculate the minimum initial balance for profit
        inibalance = balStep
        print("Calculating", end='', flush=True)
        while inibalance <= maxInitBalance:
            if inibalance % (maxInitBalance/100) == 0:
                print('.', end='', flush=True)
            
            profits, commonMults = calc_profits(days, inibalance)
            if profits is not None:
                show_profits(profits, commonMults, inibalance)
                break
                
            inibalance = inibalance + balStep     # Try next minimum initial balance
    else:
        # Calculate profitable multipliers

        profits, commonMults = calc_profits(days, initialbalance)
        if profits is not None:
            show_profits(profits, commonMults)


    if profits is None:
        print("\n-> No profits with these parameters...\n")


##############################
if __name__ == '__main__':

    validate_and_print_option()
    
    try:
        start()
    except KeyboardInterrupt:
        print("\nTerminated by CTRL+C ...")
        pass
        
    print("\n")