# Pymirokai examples

A bunch of examples to get started on using pymirokai.

## Examples

- Example to launch command on robot with or without coroutines
- a complete mini scenario
- How to cancel a mission you started
- Trigger a describe what you see
- How to send a "fake asr", so that the robot to have heard a fake sentence
- How to make the robot exit the collision state
- An example to make use of runes in a API script to create your own rune's scenario

## Setup

if you manage your python virtual environment via your IDE, skip step 1 and 2 

1. Create a virtual environment: `python -m venv .venv`
2. Activate it:
   - Windows: `.venv\Scripts\activate`
   - Unix/macOS: `source .venv/bin/activate`
3. Install pymirokai package (admin or user), for more informations read the specific README.md in the STARTER_KIT root folder.

   ```bash
   python3 -m pip install ./path/to/whl/file.whl
   ```

4. Install dependencies: `pip install -r requirements.txt`
5. you can now launch an example by using this command
   `python3 example_with_coroutine.py -i ip_of_the_robot -k api_key`
   - ip_of_the_robot is the ip of the robot or your ip if ruuning a simulation
   - api_key is the corresponding API_KEY (WIZARD_KEY)
   
6. If you want to simplify the launch, you can set the PYMIROKAI_API_KEY and ROBOT_IP in a `.env`, in your launching directory
   **take care not to share this file with people**  
      Create a `.env` file:  

   ```bash
   # be sure to put the api_key that correspond to the package installed(admin/user)
   PYMIROKAI_API_KEY=your-key-here
   # add your robot ip here if you want to test the examples on your robot and not the simulation
   #ROBOT_IP=
   ```


