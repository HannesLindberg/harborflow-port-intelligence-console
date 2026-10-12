"""HarborFlow Assignment 2 starter entry point."""
import math

def get_number(prompt, error_message="Invalid input", cast=float, min_value=0, max_value=math.inf):
    """Keep asking until the user enters something that converts with `cast`
    and is >= min_value. Never crashes on bad input."""

    while True:
        raw = input(prompt)
        try:
            value = cast(raw)
        except ValueError:
            print(error_message)
            continue

        if  value < min_value or value > max_value:
            print(error_message)
            continue

        return value
    
def main():
    """Start the terminal based application and prompt the user with options for calling other programs or closing the console.
    The cases are where the programs will be called. its based on the programs id.
    """

    run = True
    while run:
        program_id = get_number("""
        HARBORFLOW PORT INTELLIGENCE
        1. List registered vessels
        2. Inspect a vessel manifest
        3. Identify priority cargo
        4. Export a customer operations profile
        5. Find port calls by month
        6. Sanitize an incident report
        7. Analyze the longest stable event sequence
        8. Assess weather risk for upcoming calls
        9. Search incident reports
        10. Close console
        Select service: """, "Error - Select a service from 1 to 10.", int, 1, 10)

        match program_id:
            case 1:
                print("Console closed. Dispatch data remains safe.")
                run = False
            case 2:
                pass
            case 3:
                pass
            case 4:
                pass
            case 5:
               pass
            case 6:
                pass
            case 7:
                pass
            case 8:
                pass
            case 9:
                pass
            case 10:
                pass
                
if __name__ == "__main__":
    main()
