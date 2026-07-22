from datetime import date, timedelta
from typing import List, Dict, Any

class ArsNotoriaRitualEngine:
    """
    Engine to reconstruct the ritual timeline for a single Ars Notoria practice cycle.
    Harmonizes temporal markers from source excerpts into a structured schedule.
    """
    
    def __init__(self):
        # Define the canonical days of the Lunation based on source text
        # "fourth day of the Moon, the eighth and twelfth"
        self.canonical_days = [4, 8, 12]
        
        # Define prerequisites extracted from source
        self.prerequisites = {
            'state_of_mind': ['clean', 'chaste'],
            'action': ['repent of sins'],
            'desire': 'earnestly desire to cease from sinning'
        }
        
        # Define fasting duration options
        self.fasting_duration_options = [2, 3]

    def reconstruct_timeline(self) -> Dict[str, Any]:
        """
        Reconstructs the ritual timeline based on source material.
        
        Returns:
            A dictionary representing the validated timeline in ISO 8601-like format.
        """
        
        # Step 1: Define Prerequisites (Day -3 to Day -1)
        # Source: "The Operator ought to be clean, chaste, to repent of his sins..."
        # We model this as a preparation phase before the first canonical day.
        preparation_phase = {
            'start_day': '-3',
            'end_day': '-1',
            'actions': [
                'Assess spiritual state (cleanliness and chastity)',
                'Perform repentance for sins',
                'Cultivate earnest desire to cease sinning'
            ],
            'notes': 'Continuous state required throughout the cycle.'
        }

        # Step 2: Define Fasting Phase (Days -2 to -1 or Day 0)
        # Source: "it is good to fast two or three dayes"
        # We place this immediately preceding the first major rite.
        fasting_phase = {
            'start_day': '-2',
            'end_day': '-1',
            'duration_days': self.fasting_duration_options,
            'action': 'Fasting (2 or 3 days)',
            'purpose': 'To discern if desires are good or evil'
        }

        # Step 3: Define Main Rites based on Lunation Days
        # Source: "fourth day of the Moon, the eighth and twelfth"
        main_rites = []
        
        for day in self.canonical_days:
            rite_entry = {
                'day': f'+{day}',
                'action': 'Recite Oration of the four Tongues (Theos Megale)',
                'description': 'Angelic art of knowledge acquisition through prayer and notation',
                'timing_note': 'Appointed times of the Lunation'
            }
            main_rites.append(rite_entry)

        # Step 4: Define Initial Invocation
        # Source: "Now in the Name of Christ, on the first day of the Month..."
        initial_invocation = {
            'day': '+1',
            'action': 'Initial Trinitarian Invocation (Prayer in the Beginning)',
            'purpose': 'Acquire Memory, Eloquence and Understanding'
        }

        # Construct the final JSON-like structure
        timeline = {
            'ritual_cycle': {
                'name': 'Ars Notoria Practice Cycle',
                'source_basis': 'Excerpts from Lemegeton / Treatise on Spiritual and Secret Experiments',
                'preparation': [
                    {'day': '-3', 'action': 'Begin state of cleanliness and chastity'},
                    {'day': '-2', 'action': 'Perform repentance; initiate fasting (2-3 days)'}
                ],
                'main_rites': main_rites,
                'initial_invocation': initial_invocation,
                'post_rite_notes': [
                    "Read in appointed times of the Lunation",
                    "Look into the Note with fear, silence and trembling"
                ]
            }
        }

        return timeline


def main():
    """
    Main execution function to demonstrate the ritual engine.
    """
    print("Ars Notoria Ritual Engine initialized")
    
    # Create an instance of the engine
    engine = ArsNotoriaRitualEngine()
    
    # Reconstruct and display the timeline
    timeline = engine.reconstruct_timeline()
    
    import json
    print(json.dumps(timeline, indent=2))


if __name__ == "__main__":
    main()