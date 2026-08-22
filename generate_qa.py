import os
import json
from google import genai

client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

with open('system/progress_tracker.json', 'r') as f:
    tracker = json.load(f)

if tracker.get('status') == "completed":
    print("🎉 ધોરણ 5 અને 6 નું સંપૂર્ણ ઓટોમેશન પૂરું થઈ ગયું છે!", flush=True)
    exit(0)

# ---------------------------------------------------------
# સિલેબસ ડેટાબેઝ (ધોરણ 5 અને 6 ના તમામ વિષયો અને તેના પ્રકરણોની સંખ્યા)
# ---------------------------------------------------------
syllabus = {
    5: [
        {"name": "Maths", "guj_name": "ગણિત ગમ્મત", "chapters": 14},
        {"name": "EVS", "guj_name": "પર્યાવરણ (આસપાસ)", "chapters": 22},
        {"name": "Gujarati", "guj_name": "ગુજરાતી (કેકારવ)", "chapters": 10},
        {"name": "English", "guj_name": "અંગ્રેજી", "chapters": 6},
        {"name": "Hindi", "guj_name": "હિન્દી", "chapters": 16}
    ],
    6: [
        {"name": "Maths", "guj_name": "ગણિત", "chapters": 12},
        {"name": "Science", "guj_name": "વિજ્ઞાન", "chapters": 11},
        {"name": "SS", "guj_name": "સામાજિક વિજ્ઞાન", "chapters": 17},
        {"name": "Gujarati", "guj_name": "ગુજરાતી (પલાશ)", "chapters": 10},
        {"name": "English", "guj_name": "અંગ્રેજી", "chapters": 8},
        {"name": "Hindi", "guj_name": "હિન્દી", "chapters": 10},
        {"name": "Sanskrit", "guj_name": "સંસ્કૃત", "chapters": 9}
    ]
}

standards = [5, 6]

# ---------------------------------------------------------
# પ્રશ્નોના પ્રકાર અને ટાર્ગેટ (નાના પ્રશ્નો 60+, મોટા 10+)
# ---------------------------------------------------------
question_types = [
    {"id": "MCQs", "name": "બહુવિકલ્પી પ્રશ્નો (MCQs)", "marks": 1, "min_count": 60},
    {"id": "FillBlanks", "name": "ખાલી જગ્યા પૂરો", "marks": 1, "min_count": 60},
    {"id": "TrueFalse", "name": "ખરા ખોટા જણાવો", "marks": 1, "min_count": 60},
    {"id": "MatchPairs", "name": "જોડકાં જોડો", "marks": 1, "min_count": 60},
    {"id": "1_Mark", "name": "એક વાક્યમાં ઉત્તર", "marks": 1, "min_count": 60},
    {"id": "2_Marks", "name": "બે ગુણના ટૂંક જવાબી પ્રશ્નો", "marks": 2, "min_count": 10},
    {"id": "3_Marks", "name": "ત્રણ ગુણના મુદ્દાસર પ્રશ્નો", "marks": 3, "min_count": 10},
    {"id": "4_Marks", "name": "ચાર ગુણના વિસ્તૃત પ્રશ્નો", "marks": 4, "min_count": 10}
]

# હાલનું સ્ટેટસ મેળવવું
std_idx = tracker['current_std_index']
sub_idx = tracker['current_subject_index']
type_idx = tracker['current_type_index']
ch_num = tracker['current_chapter']

current_std = standards[std_idx]
current_subject = syllabus[current_std][sub_idx]
current_q_type = question_types[type_idx]
max_chapters = current_subject["chapters"]

print(f"Generating {current_q_type['name']} for Std {current_std} {current_subject['name']} Chapter {ch_num}...", flush=True)

# પ્રકાર મુજબ ખાસ નિયમો
type_specific_rules = ""
if current_q_type['id'] == "MCQs":
    type_specific_rules = "દરેક પ્રશ્ન સાથે 4 વિકલ્પો (A, B, C, D) ફરજિયાત આપવા."
elif current_q_type['id'] == "FillBlanks":
    type_specific_rules = "દરેક ખાલી જગ્યાના અંતે કૌંસમાં 3 વિકલ્પો આપવા."
elif current_q_type['id'] == "TrueFalse":
    type_specific_rules = "વિધાન સાચું છે કે ખોટું તે જણાવો અને ખોટું હોય તો કારણ આપો."
elif current_q_type['id'] == "MatchPairs":
    type_specific_rules = "વિભાગ A અને વિભાગ B ના જોડકાં આપવા અને જવાબમાં સાચી જોડ આપવી."

prompt = f"""
તમે ગુજરાત બોર્ડ (GSEB) ના એક્સપર્ટ શિક્ષક છો. 
તમારે ધોરણ {current_std}, વિષય: {current_subject['guj_name']}, પ્રકરણ: {ch_num} ના નવા NCERT સિલેબસ મુજબ પ્રશ્નો બનાવવાના છે.

પ્રશ્નનો પ્રકાર: {current_q_type['name']} ({current_q_type['marks']} માર્ક)

અત્યંત કડક નિયમો (STRICT QUALITY CONTROL):
1. પ્રશ્નોની સંખ્યા (TARGET): ઓછામાં ઓછા {current_q_type['min_count']} પ્રશ્નો ફરજિયાત બનાવવાના છે. જો આ પ્રકરણ મોટું હોય તો {current_q_type['min_count']} થી વધુ પ્રશ્નો બનાવવાની પૂરી કોશિશ કરવી.
2. પ્રકાર મુજબ શરત: {type_specific_rules}
3. નો-રીપીટેશન અને એક્ઝેક્ટ લેવલ: {current_q_type['marks']} ગુણના પ્રશ્નોનું લેવલ બરાબર તેટલા જ માર્કસનું હોવું જોઈએ. 4 માર્કના મોટા પ્રશ્નો ક્યારેય 2 માર્કમાં ન આવવા જોઈએ અને 2 માર્કના ટૂંકા પ્રશ્નો 4 માર્કમાં ન આવવા જોઈએ. પ્રશ્નો એકબીજામાં રીપીટ ન થવા જોઈએ.
4. સંપૂર્ણ જવાબ અને ટ્રીક: દરેક પ્રશ્નની સાથે તેનો સચોટ જવાબ અને તેને યાદ રાખવા માટે '💡 નિતેશ સરની શોર્ટકટ ટ્રીક (NJ Classes)' ફરજિયાત હોવી જોઈએ.

ફોર્મેટ (STRICT JSON FORMAT):
કોઈપણ જાતના વેરીએબલ વગર માત્ર નીચે મુજબનું JSON Object આપવું:
{{
  "chapterName": "પ્રકરણ {ch_num}",
  "chapterTitle": "પ્રકરણનું નામ",
  "questionType": "{current_q_type['name']}",
  "qa_list": [
    {{
      "questionNumber": "પ્રશ્ન 1",
      "question": "અહીં પ્રશ્ન લખવો...",
      "answer": "<div style='background-color:#f0f8ff; padding:15px; border-left:5px solid #16a085; border-radius:8px;'><p><strong>ઉકેલ/જવાબ:</strong> અહીં સાચો જવાબ લખવો.</p><hr><p style='color:#d32f2f; font-weight:bold;'>💡 નિતેશ સરની શોર્ટકટ ટ્રીક: અહીં યાદ રાખવાની ટ્રીક લખવી...</p></div>"
    }}
  ]
}}
"""

print("Searching for live text models from your API account...", flush=True)
valid_models = []
try:
    for model in client.models.list():
        if hasattr(model, 'supported_actions') and "generateContent" in model.supported_actions:
            name = model.name.lower()
            if not any(word in name for word in ['video', 'audio', 'tts', 'vision', 'image', 'exp', 'learnlm', 'embedding', 'aqa']):
                valid_models.append(model.name)
except Exception as e:
    print(f"Error fetching models: {e}", flush=True)

valid_models.sort(key=lambda x: ('flash' not in x.lower(), x))
output_data = ""

for m in valid_models[:3]:
    try:
        print(f"⏳ Pending: {m} મોડલ દ્વારા ઓછામાં ઓછા {current_q_type['min_count']} પ્રશ્નો બની રહ્યા છે...", flush=True)
        response = client.models.generate_content(model=m, contents=prompt)
        raw_output = response.text.strip()
        
        if "{" in raw_output and "}" in raw_output:
            raw_output = raw_output[raw_output.find("{") : raw_output.rfind("}") + 1]
            
        output_data = raw_output.strip()
        print(f"✅ Success! ડેટા બની ગયો છે.", flush=True)
        break
    except Exception as e:
        print(f"❌ Failed with {m}. Error: {e}", flush=True)

if not output_data:
    print("Error: બધી જ ટ્રાય ફેલ ગઈ છે.", flush=True)
    exit(1)

# ફોલ્ડર સ્ટ્રક્ચર: Std5/Maths/
folder_path = f"Std{current_std}/{current_subject['name']}"
os.makedirs(folder_path, exist_ok=True)

q_id = current_q_type['id']
file_path = f"{folder_path}/{current_subject['name']}_{q_id}.js"

mode = 'a' if os.path.exists(file_path) else 'w'
with open(file_path, mode, encoding='utf-8') as f:
    if mode == 'w':
        f.write(f"var Std{current_std}_{current_subject['name']}_{q_id} = {{\n")
        f.write(f'"{ch_num}": ' + output_data + '\n')
    else:
        f.write(f',\n"{ch_num}": ' + output_data + '\n')

# ---------------------------------------------------------
# ટ્રાન્ઝિશન લોજીક (હોરીઝોન્ટલ સ્કેનિંગ: પ્રકરણ -> પ્રશ્ન પ્રકાર -> વિષય -> ધોરણ)
# ---------------------------------------------------------
tracker['current_chapter'] += 1

if tracker['current_chapter'] > max_chapters:
    tracker['current_chapter'] = 1
    tracker['current_type_index'] += 1
    
    if tracker['current_type_index'] >= len(question_types):
        tracker['current_type_index'] = 0
        tracker['current_subject_index'] += 1
        
        if tracker['current_subject_index'] >= len(syllabus[current_std]):
            tracker['current_subject_index'] = 0
            tracker['current_std_index'] += 1
            
            if tracker['current_std_index'] >= len(standards):
                tracker['status'] = "completed"
                tracker['current_std_index'] -= 1 # એરર અટકાવવા

with open('system/progress_tracker.json', 'w') as f:
    json.dump(tracker, f, indent=4)

print("Task Completed Successfully! Perfect Master Format Applied.", flush=True)
