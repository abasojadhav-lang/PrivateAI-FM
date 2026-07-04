import random

class DJScriptEngine:
    def generate_dj_commentary(self, personality: str, song_title: str, artist: str) -> str:
        personality = personality.lower()
        
        # Professional
        if personality == "professional":
            templates = [
                f"You're listening to PrivateFM AI. That was '{song_title}' by {artist}. Up next, another carefully selected track.",
                f"This is PrivateFM AI, your personal radio station. That was '{song_title}'. We continue our broadcast with this next song.",
                f"That was the sound of {artist} performing '{song_title}'. Up next, a selection tailored to your profile.",
            ]
        # Funny
        elif personality == "funny":
            templates = [
                f"PrivateFM AI! Hope you liked '{song_title}' by {artist} as much as my cat did. Let's roll with the next track!",
                f"That was '{song_title}' by {artist}. Legend has it that song was written about my bad cooking. Let's keep it moving!",
                f"You're listening to your music peon's choice. That was '{song_title}'. Up next: a song guaranteed to make you dance (or at least nod your head).",
            ]
        # Sarcastic
        elif personality == "sarcastic":
            templates = [
                f"Well, that was '{song_title}' by {artist}. Truly a masterpiece of our generation. Prepare your ears for what's next.",
                f"PrivateFM AI, where I get paid in electricity. That was {artist} with '{song_title}'. Moving on before I get emotional.",
                f"Ah, '{song_title}'. Simply breathtaking. Let's rush into the next song before we actually start listening.",
            ]
        # Calm
        elif personality == "calm":
            templates = [
                f"Let the sound settle. That was '{song_title}' by {artist}. Relax your mind as we glide into this next melody.",
                f"Peaceful sounds on PrivateFM AI. '{song_title}' by {artist}. Take a deep breath, and enjoy the rhythm.",
                f"Gliding along. That was {artist} with '{song_title}'. Here is another quiet track for your day.",
            ]
        # Energetic
        elif personality == "energetic":
            templates = [
                f"BOOM! PrivateFM AI! That was the massive track '{song_title}' by {artist}! Let's keep this fire burning with this next pick!",
                f"YEAH! That was '{song_title}' by {artist}! absolute banger! Get ready to jump because this next one is even louder!",
                f"Energy levels off the charts! '{song_title}' by {artist} just rocked the station! Let's blast right into the next one!",
            ]
        # Friendly/Default
        else:
            templates = [
                f"You're listening to PrivateFM AI. That was a great track: '{song_title}' by {artist}. Coming up next is a song just for you.",
                f"Hey, hope you're enjoying your radio. That was '{song_title}'. Let's jump into the next song together.",
                f"PrivateFM AI, your friendly music station. '{song_title}' by {artist}. Here is what we have lined up next.",
            ]
            
        return random.choice(templates)

    def generate_weather_report(self, personality: str, location: str = "Pune") -> str:
        personality = personality.lower()
        
        if personality == "professional":
            return f"Weather update for {location}: The current temperature is 29 degrees Celsius under mostly clear skies, with humidity at 60%."
        elif personality == "funny":
            return f"Weather in {location} is 29 degrees. That is hot enough to melt chocolate in your pockets, folks. Wear sunscreen or stay indoors!"
        elif personality == "sarcastic":
            return f"Weather update: {location} is currently 29 degrees. Shockingly, the sun is doing its job. Back to you inside."
        elif personality == "calm":
            return f"A gentle breeze sweeps through {location} today. Peaceful, sunny skies at 29 degrees. Take a moment to enjoy the day."
        elif personality == "energetic":
            return f"IT IS SIZZLING IN {location}! 29 DEGREES OF PURE SUNSHINE! PERFECT DAY TO GET OUT AND CRUSH IT!"
        else:
            return f"Here is the local weather for {location}: It's currently 29 degrees with clear blue skies. Have a wonderful day!"

    def generate_news_brief(self, personality: str) -> str:
        personality = personality.lower()
        
        if personality == "professional":
            return "In national news: Financial indices reached record highs today following strong performance indicators in the tech sector."
        elif personality == "funny":
            return "Breaking news: Scientists report that people who drink morning coffee are 100% more likely to be awake. Incredible discovery."
        elif personality == "sarcastic":
            return "Headline today: Billionaire claims that money cannot buy happiness, shortly after purchasing his fifth superyacht. Fascinating."
        elif personality == "calm":
            return "In local news: Community volunteers gathered at the city garden to plant trees, bringing green and peaceful spaces to life."
        elif personality == "energetic":
            return "BREAKING NEWS! TECH SECTOR IS EXPLODING! MARKET INDEXES ARE SOARING HIGHER THAN EVER! WHAT A TIME TO BE ALIVE!"
        else:
            return "Here is your quick news brief: Tech companies announced major green energy initiatives to reduce carbon emissions."

    def generate_traffic_report(self, personality: str, location: str = "Pune") -> str:
        personality = personality.lower()
        
        if personality == "professional":
            return f"Traffic update for {location}: Major arteries are flowing smoothly with minor delays reported on the main expressway."
        elif personality == "funny":
            return f"Traffic in {location} is currently bumper-to-bumper. Great time to practice your car karaoke, folks!"
        elif personality == "sarcastic":
            return f"Traffic update: The highway is currently a parking lot. Good thing we all love sitting in our cars doing nothing."
        elif personality == "calm":
            return f"Traffic is moving slowly and peacefully today in {location}. Relax, take your time, and travel safely."
        elif personality == "energetic":
            return f"TRAFFIC UPDATE! ROAD IS CLEAR AND FLOWING! BLAST YOUR MUSIC AND CRUISE HOME SAFE!"
        else:
            return f"Here is the local traffic update for {location}: Roads are mostly clear with normal commute times today."

script_engine = DJScriptEngine()
