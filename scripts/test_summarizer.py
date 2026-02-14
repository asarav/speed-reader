import sys
sys.path.insert(0, 'src')
from speed_reader.utils.summarizer import summarize_text

text_with_punct = '''On the way back to the village, we got off the bus too early, finding ourselves at an intersection with a restaurant, a gas station, and a sign that read KÁL, 6 KM . I suggested that we walk, but Reni said that six kilometers was very far and that I would be tired. “I’ve an idea,” she said. “My boyfriend’s telephone.” “Your boyfriend’s telephone?” “That is only one kilometer. Come.” We left the highway, walking down a narrow paved road that turned into a dirt road. After about half an hour, we arrived at an orange and brown house with a BITING DOG sign. Reni knocked at the gate. An ugly fist-faced black dog leaped out of a shed, bolted across the yard, and threw itself slavering at the fence. “Oh, Milord!” Reni thrust her hands through the gate and seized the dog’s head in such a way that it became incapable—though not, I thought, undesirous—of sinking its teeth in her person. Its hindquarters thrashed in the air. “Milord is a very nice dog,” Reni said. Slobber dripped down her wrist. A woman came out with a plastic basket full of laundry, noticed Reni, frowned, and went back inside. “That is my boyfriend’s mother,” Reni said. “She does not love me.” I nodded. “But she is helpless,” Reni continued. “Her son loves me. Now she will call him.” “Wouldn’t your boyfriend’s mother let us use the telephone?” I asked, some minutes later. “Oh, no!” said Reni. “She thinks I am . . . a very bad girl. I don’t know in English.” She was still holding the dog’s head, which emitted a low growling sound. I offered to knock on the door and ask if I could use the telephone, but Reni said the mother was very suspecting and would think I was also bad. After we had'''

# Simulate word-list input (no punctuation)
words = text_with_punct.replace('\n',' ').split()
word_list_text = ' '.join(words)

print('--- Summary from punctuation text ---')
print(summarize_text(text_with_punct, max_sentences=6))
print('\n--- Summary from word-list text ---')
print(summarize_text(word_list_text, max_sentences=6))
