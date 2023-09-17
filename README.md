# ptfs-joystick
A project dedicated for the Throttlemaster Airbus Edition Captain Pack that lets you control PTFS (Pilot Training Flight Simulator) using no other than the joystick aswell as the throttle, along with other features.

# The journey
### 11th September 2023
This is the day I got the Throttlemaster Airbus Edition Captain Pack. Later that day I was playing PTFS and stumbled across a thought of "maybe I could make it work with PTFS"

Did a little testing of trying to get the hardware to show up in Python, but I couldn't find anything yet. I tried the `inputs` libary but, well.. that's 7 years out of date and doesn't work for me.

### 12th September 2023
This is also very inconveniently my first day back at College. Throughout the day I thought of ways I could detect the hardware.<br/>
Did a bit of research throughout the day I was there, and came across **[pyglet](https://github.com/pyglet/pyglet)**, an actively maintained multimedia libary for Python. Perfect!

Later that day when I got home, I tried it out, and successfully detected the joystick and throttle!<br/>
The rest of the day went like this:
- 18:15 - detected the joystick & throttle using pyglet.
- 18:30 - successfully detected joystick axis movements for both UP, DOWN, LEFT, RIGHT and also the rudder.
- 18:40 - alot of ideas sparked into my brain at this point. Altitude Hold for the red button on the joystick? Reverse thrust for pushback?
- 19:00 - me testing in-game where the cursor should be to represent an idle joystick. (center of screen roughly)
- 19:50 - Huh! PyAutoGui doesn't work?!?!? What's going on wtf!??!
  - Yeah. Did some research on "pyautogui move not working for game", turns out it's some complicated stuff to do with DirectX and etc.
  - BUT DO NOT FEAR! FOR **[pydirectinput](https://github.com/learncodebygaming/pydirectinput)** IS HERE!
    - It's a fork of pyautogui, however supports DirectX mouse movements. Perfect! It works!
- 20:40 - Successfully made mouse movements react to my joystick. WOOHOO!
- 21:00 - Around here I was probably implementing ground VS airborne state.
  - Airborne for full joystick and rudder control, and ground for only rudder control - with this being a toggleable mode by a button on my joystick.
- 21:30 - Gear toggle, Altitude Hold aka Autopilot, Flaps integration
- 22:00 - Twin-Engine and Single-Engine support. Will indicate engine start failure if knob is not set to IGN/START.
- 22:30 - Throttle control. If one throttle is MAX and the other is IDLE for a Twin-Engine, the result throttle is 50%. For a single engine, only the first throttle lever is taken into account. Not the second one.
- 23:00 - Reverse thrust for pushback.
- 23:59 - First fully integrated test flight using a joystick and throttle.
  - This test flight went seemingly well from taxi and takeoff to landing. I noticed a few things I could improve, especially throttle. I had it set to IDLE however it was showing 2% on screen.
  - As of here, throttle control was determined by holding down the "w" key for 0.033s which equals 1% throttle increase/decrease.
  - And no. It's not as simple as `for i in range(100): pydirectinput.press("w", _pause=False)`. It's too slow. Even with `_pause=False`.

### 13th September 2023
Today, I figured of a new idea I could do. Usually an aircraft taxies under its own power. Why should I need to increase throttle to taxi?<br/>
This is where my parking brake idea came to light.

I figured I'll implement it so if the parking brake is OFF (and the engines are on), the aircraft with increase its own throttle automatically to 15%, for taxi.

And if the parking brake is ON, a -15% throttle deduction is in place. Meaning throttle can manually be increased to 15%, it will do nothing. 16%, and it will go to 1%.

With pushback and parking brake ON, the maximum pushback speed is 8% (1 knot).<br/>
With pushback and parking brake OFF, the maximum pushback speed is 32% (10 knots)

Later that day, at around 20:00, I did a test flight.<br/>
Spoiler: Didn't work! Throttle never even increased in the first place, however the parking brake still worked (meaning I could taxi, but not takeoff with increased throttle).

Obviously a logic error somewhere in the code, however, this wasn't really what I was concerned about.

Since I set the taxispeed with parking brake OFF to 15%, I expected it to be at 15%.. but it wasn't!<br/>
I stopped the test flight, and went back to throttle testing. I then ran a "w" key press for 0.033 * 15 seconds. Should be 15% throttle right? Nope! It was 18%.<br/>
I then ran a key press for 0.033 * 90 seconds. Should be.. 93% throttle then? Nope! It was 90%. **I was pretty bamboozled at this point.**

After this, I spent the next hour messing around with throttle and adjusting the 1% throttle increase duration (0.033s).

### 14th September 2023
During the course of today, I spent ways I could improve throttle control.<br/>
A thought that came to my mind is set up a script that detects a "w" key press and instantly starts a stopwatch, with no time.sleep inbetween prints (meaning it's basically printing every 0.001s.<br/>
With this script, I could then set up OBS to capture the script output and also Roblox at the same time as I increase my throttle from 1% to 100%.<br/>
This way I have millisecond precision for how long it takes to get to each throttle, from 1% to 100%.

I could then analyze this by using video editing software to view EACH frame.<br/>
I ended up with Adobe Express, since it's free and easy to use for what I want to do, which is simply view frames.

I then spent essentially the rest of this day analyzing each frame and logging the amount of time it takes to get to 1% throttle, 2% throttle, 3% throttle, all the way up to 30% throttle.

I also noticed that no matter how much I altered the millisecond duration, for some throttle percentages, it simply wasn't accurate (1% throttle difference, mostly).<br/>
This is when I knew, I'd need not only this system - but another system backed up ontop of this system, to get the throttle 100% ACCURATE.

**Template Matching.** This is what I knew I'd need to accurately control this throttle system.<br/>
I know this will take a long time though to setup (all the templates), however it'll hopefully in the long run be worth it.

I then did some research on libaries I can use for screenshotting certain parts of a screen.<br/>
I then stumbled across **[pyscreenshot](https://github.com/ponty/pyscreenshot)**, which worked perfectly.<br/>
I then figured out the monitor coordinates for the throttle box in PTFS.

### 15th September 2023, jesus christ finally it's Friday that took ages
Nothing majorly interesting today. I didn't have that much time to work on continuing the throttle improvements.<br/>
However, I was able to continue covering millisecond throttle durations from throttles 30% to 50%. Halfway point!

### 16th September 2023
YAY. Finally finished logging the rest of the exact millisecond durations from throttles 50% to 100%.

So now I've done that, I'll worry about implementation later.

Now I'm moving onto template matching.<br/>
Firstly, I wanted to make sure I was actually getting the screenshot of the throttle area the fastest way - since I remember reading a TLDR to use Pillow instead of pyscreenshot.. on the pyscreenshot github.

So I timed both `pyscreenshot.grab` and `PIL.ImageGrab`, and it turns out `pyscreenshot.grab` computes at 0.17s speed whereas `PIL.ImageGrab` computes at 0.03s speed.<br/>
Obviously I'm going to be moving over to PIL from now on.

After doing extensive testing, I have settled with using adaptive thresholding to capture the white text that shows the throttle value. Normal thresholding simply didn't produce promising results.

Also.. turns out there's an even faster way to capture a part of a screen.<br/>
The **[mss](https://github.com/BoboTiG/python-mss)** module, which I've used to record my screen and focus on the throttle area and apply adaptive thresholding to it, so I can visually see how it changes depending on the background.

After many parameter modifications, I settled with this:
```py
thresh = cv.adaptiveThreshold(npimg, 255, cv.ADAPTIVE_THRESH_GAUSSIAN_C, cv.THRESH_BINARY, 9, -40)
```

### 17th September 2023
Soo.. I've applied thresholding. OK. Now I need the throttle VALUE.

I asked chatgpt what I was trying to do, and it recommended I use **[pytesseract](https://github.com/madmaze/pytesseract)** which uses Google's tesseract OCR technology.<br/>
I tried it out, and it could detect simply throttle values like "100%" however values like "97%" it straight up didn't detect and the same with all values less than 10.<br/>
So tesseract is going to be a no, since it's unreliable.

I then moved a idea of my own, "template matching" but it's not using `cv.matchTemplate` since the template and the orignal image are going to be the exact same dimensions with the exact same threshold applied.

I then created templates for throttle values 0% to 100% and kept them inside a templates folder.

Instead, I'd use a `cv.bitwise_xor` operation between the template and the on-screen image to get the amount of non-matching pixels between the two images.<br/>
The idea of this is, I will loop through each template and perform the XOR operation on the on-screen image and then store the amount of **non-zero values** it had.

The template that has the LEAST amount of non-zero values, AKA the LEAST amount of difference between the template and the on-screen image, would be the throttle value.

I then tested this, and to my surprised and utter RELIEF, IT WORKS! I can now detect the throttle value from simply ON SCREEN PIXELS.

I then RUSHED EAGERLY to implement this into my main code.<br/>
But first, remember the exact millisecond durations for each throttle value? Yep, that hasn't disappeared. Still need that.<br/>

The throttle increase/decrease system in my main script will work like this:<br/>
- Hold down "w" key.
- Wait for exact millisecond duration using `event.wait` (`threading.Event`)
  - During this, it should break anytime if a new throttle value is needed.
    - For example, I set throttle to 10%. During the throttle change, I change it to 15%. That's when it should break.
  - If it does break, then it grabs the CURRENT throttle value using the thresholding technique.
  - It will then re-do this process, but for the new throttle value.
- Release "w" key.

For this, I need a way to interrupt a `event.wait` operation for when holding down the "w" key and a new throttle value appears.<br/>
I went to stack overflow, and found that using the following code structure will work.
```py
# main thread
while not event.is_set()
  event.wait(60)
  break
event.clear() # clean-up code, allowing the event object to be used again.

# other thread
event.set() # will break the event.wait()
```

Excellent! I now implemented this in the main code.<br/>
I had another idea after I finished doing this. Spoilers! What to do with them??<br/>
Well, I set the maximum pushback value to 32%, because that's the maximum pushback speed on the ground.

With the spoilers, I will fill the gap from 32% to 100% but ONLY when airborne and in reverse thrust mode.<br/>
With the spoilers without reverse thrust, throttle will be reduced by 10% (if spoilers are at 100%).
