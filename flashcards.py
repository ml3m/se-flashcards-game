import pygame
import re
import random
import textwrap
import sys

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 700
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (70, 130, 200)
LIGHT_BLUE = (173, 216, 230)
GRAY = (128, 128, 128)
GREEN = (34, 139, 34)
RED = (220, 20, 60)

# Fonts
font_large = pygame.font.Font(None, 36)
font_medium = pygame.font.Font(None, 28)
font_small = pygame.font.Font(None, 24)

class QuestionParser:
    def __init__(self, tex_file):
        self.tex_file = tex_file
        self.questions = []
        self.parse_questions()
    
    def clean_latex(self, text):
        """Remove LaTeX commands and clean up text"""
        # Remove common LaTeX commands
        text = re.sub(r'\\textbf\{([^}]*)\}', r'\1', text)
        text = re.sub(r'\\begin\{itemize\}.*?\\end\{itemize\}', '', text, flags=re.DOTALL)
        text = re.sub(r'\\begin\{enumerate\}.*?\\end\{enumerate\}', '', text, flags=re.DOTALL)
        text = re.sub(r'\\item\s*', '• ', text)
        text = re.sub(r'\\\\', '\n', text)
        text = re.sub(r'\\[a-zA-Z]+\{[^}]*\}', '', text)
        text = re.sub(r'\\[a-zA-Z]+', '', text)
        text = re.sub(r'\{([^}]*)\}', r'\1', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()
    
    def parse_questions(self):
        """Parse questions from the LaTeX file"""
        try:
            with open(self.tex_file, 'r', encoding='utf-8') as file:
                content = file.read()
            
            # Find all questionbox blocks
            question_pattern = r'\\begin\{questionbox\}(.*?)\\end\{questionbox\}'
            questions = re.findall(question_pattern, content, re.DOTALL)
            
            # Find corresponding answers
            for i, question in enumerate(questions):
                question_clean = self.clean_latex(question)
                
                # Find the answer that follows this question
                question_pos = content.find(f'\\begin{{questionbox}}{question}\\end{{questionbox}}')
                next_question_pos = content.find('\\begin{questionbox}', question_pos + 1)
                
                if next_question_pos == -1:
                    answer_section = content[question_pos + len(f'\\begin{{questionbox}}{question}\\end{{questionbox}}'):]
                else:
                    answer_section = content[question_pos + len(f'\\begin{{questionbox}}{question}\\end{{questionbox}}'):next_question_pos]
                
                # Clean up the answer section
                answer_section = re.sub(r'\\begin\{questionbox\}.*?\\end\{questionbox\}', '', answer_section, flags=re.DOTALL)
                answer_section = re.sub(r'\\subsection\{.*?\}', '', answer_section)
                answer_section = re.sub(r'\\section\{.*?\}', '', answer_section)
                answer_section = re.sub(r'\\newpage', '', answer_section)
                answer_section = re.sub(r'\(Source:.*?\)', '', answer_section)
                
                answer_clean = self.clean_latex(answer_section)
                
                if question_clean and answer_clean:
                    self.questions.append({
                        'question': question_clean,
                        'answer': answer_clean
                    })
        
        except FileNotFoundError:
            print(f"Error: Could not find file {self.tex_file}")
            sys.exit(1)
        except Exception as e:
            print(f"Error parsing file: {e}")
            sys.exit(1)

class Flashcard:
    def __init__(self, question, answer):
        self.question = question
        self.answer = answer
        self.showing_answer = False
    
    def flip(self):
        self.showing_answer = not self.showing_answer
    
    def get_current_text(self):
        return self.answer if self.showing_answer else self.question

class FlashcardApp:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("SE Forms Questions - Flashcards")
        self.clock = pygame.time.Clock()
        
        # Parse questions
        self.parser = QuestionParser('SE-FORMS-QUESTIONS.tex')
        if not self.parser.questions:
            print("No questions found in the LaTeX file!")
            sys.exit(1)
        
        # Create flashcards
        self.flashcards = [Flashcard(q['question'], q['answer']) for q in self.parser.questions]
        random.shuffle(self.flashcards)
        
        self.current_index = 0
        self.current_card = self.flashcards[self.current_index] if self.flashcards else None
        
        # UI elements
        self.card_rect = pygame.Rect(50, 100, SCREEN_WIDTH - 100, SCREEN_HEIGHT - 200)
        self.next_button = pygame.Rect(SCREEN_WIDTH - 120, SCREEN_HEIGHT - 80, 100, 40)
        self.prev_button = pygame.Rect(20, SCREEN_HEIGHT - 80, 100, 40)
        self.shuffle_button = pygame.Rect(SCREEN_WIDTH // 2 - 50, SCREEN_HEIGHT - 80, 100, 40)
    
    def wrap_text(self, text, font, max_width):
        """Wrap text to fit within the given width"""
        words = text.split(' ')
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + word + " "
            if font.size(test_line)[0] <= max_width:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line.strip())
                current_line = word + " "
        
        if current_line:
            lines.append(current_line.strip())
        
        return lines
    
    def draw_card(self):
        """Draw the current flashcard"""
        if not self.current_card:
            return
        
        # Card background
        pygame.draw.rect(self.screen, WHITE, self.card_rect)
        pygame.draw.rect(self.screen, BLUE, self.card_rect, 3)
        
        # Card content
        text = self.current_card.get_current_text()
        font = font_medium if len(text) < 200 else font_small
        
        lines = self.wrap_text(text, font, self.card_rect.width - 40)
        
        # Calculate total height of text
        line_height = font.get_height() + 5
        total_height = len(lines) * line_height
        
        # Start position (centered vertically)
        start_y = self.card_rect.y + (self.card_rect.height - total_height) // 2
        
        for i, line in enumerate(lines):
            if start_y + i * line_height > self.card_rect.bottom - 40:
                break  # Don't draw outside the card
            
            text_surface = font.render(line, True, BLACK)
            text_rect = text_surface.get_rect()
            text_rect.centerx = self.card_rect.centerx
            text_rect.y = start_y + i * line_height
            self.screen.blit(text_surface, text_rect)
        
        # Draw card type indicator
        card_type = "ANSWER" if self.current_card.showing_answer else "QUESTION"
        color = GREEN if self.current_card.showing_answer else BLUE
        type_surface = font_small.render(card_type, True, color)
        type_rect = type_surface.get_rect()
        type_rect.topright = (self.card_rect.right - 10, self.card_rect.top + 10)
        self.screen.blit(type_surface, type_rect)
        
        # Draw click to flip instruction
        if not self.current_card.showing_answer:
            instruction = "Click card to see answer"
        else:
            instruction = "Click card to see question"
        
        instruction_surface = font_small.render(instruction, True, GRAY)
        instruction_rect = instruction_surface.get_rect()
        instruction_rect.centerx = self.card_rect.centerx
        instruction_rect.bottom = self.card_rect.bottom - 10
        self.screen.blit(instruction_surface, instruction_rect)
    
    def draw_buttons(self):
        """Draw navigation buttons"""
        # Previous button
        prev_color = GRAY if self.current_index == 0 else BLUE
        pygame.draw.rect(self.screen, prev_color, self.prev_button)
        prev_text = font_small.render("Previous", True, WHITE)
        prev_text_rect = prev_text.get_rect(center=self.prev_button.center)
        self.screen.blit(prev_text, prev_text_rect)
        
        # Next button
        next_color = GRAY if self.current_index >= len(self.flashcards) - 1 else BLUE
        pygame.draw.rect(self.screen, next_color, self.next_button)
        next_text = font_small.render("Next", True, WHITE)
        next_text_rect = next_text.get_rect(center=self.next_button.center)
        self.screen.blit(next_text, next_text_rect)
        
        # Shuffle button
        pygame.draw.rect(self.screen, GREEN, self.shuffle_button)
        shuffle_text = font_small.render("Shuffle", True, WHITE)
        shuffle_text_rect = shuffle_text.get_rect(center=self.shuffle_button.center)
        self.screen.blit(shuffle_text, shuffle_text_rect)
    
    def draw_info(self):
        """Draw app info and current card number"""
        title = "SE Forms Questions - Flashcards"
        title_surface = font_large.render(title, True, BLUE)
        title_rect = title_surface.get_rect()
        title_rect.centerx = SCREEN_WIDTH // 2
        title_rect.y = 20
        self.screen.blit(title_surface, title_rect)
        
        # Card counter
        if self.flashcards:
            counter = f"Card {self.current_index + 1} of {len(self.flashcards)}"
            counter_surface = font_medium.render(counter, True, BLACK)
            counter_rect = counter_surface.get_rect()
            counter_rect.centerx = SCREEN_WIDTH // 2
            counter_rect.y = 60
            self.screen.blit(counter_surface, counter_rect)
    
    def next_card(self):
        """Go to next card"""
        if self.current_index < len(self.flashcards) - 1:
            self.current_index += 1
            self.current_card = self.flashcards[self.current_index]
            self.current_card.showing_answer = False
    
    def prev_card(self):
        """Go to previous card"""
        if self.current_index > 0:
            self.current_index -= 1
            self.current_card = self.flashcards[self.current_index]
            self.current_card.showing_answer = False
    
    def shuffle_cards(self):
        """Shuffle the cards"""
        random.shuffle(self.flashcards)
        self.current_index = 0
        self.current_card = self.flashcards[self.current_index]
        self.current_card.showing_answer = False
    
    def handle_click(self, pos):
        """Handle mouse clicks"""
        if self.card_rect.collidepoint(pos):
            # Click on card - flip it
            if self.current_card:
                self.current_card.flip()
        elif self.next_button.collidepoint(pos):
            # Next button
            if self.current_index < len(self.flashcards) - 1:
                self.next_card()
        elif self.prev_button.collidepoint(pos):
            # Previous button
            if self.current_index > 0:
                self.prev_card()
        elif self.shuffle_button.collidepoint(pos):
            # Shuffle button
            self.shuffle_cards()
    
    def run(self):
        """Main game loop"""
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        # Space bar flips card
                        if self.current_card:
                            self.current_card.flip()
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_n:
                        # Right arrow or 'n' for next
                        self.next_card()
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_p:
                        # Left arrow or 'p' for previous
                        self.prev_card()
                    elif event.key == pygame.K_s:
                        # 's' for shuffle
                        self.shuffle_cards()
            
            # Draw everything
            self.screen.fill(LIGHT_BLUE)
            self.draw_info()
            self.draw_card()
            self.draw_buttons()
            
            pygame.display.flip()
            self.clock.tick(60)
        
        pygame.quit()

if __name__ == "__main__":
    app = FlashcardApp()
    app.run() 