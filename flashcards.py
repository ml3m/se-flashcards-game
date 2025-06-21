import pygame
import json
import random
import math
import sys
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60

# Modern Color Palette
COLORS = {
    'bg_primary': (15, 17, 26),           # Dark navy background
    'bg_secondary': (25, 28, 42),         # Slightly lighter navy
    'card_front': (255, 255, 255),        # Clean white for questions
    'card_back': (59, 130, 246),          # Modern blue for answers
    'text_primary': (17, 24, 39),         # Dark text
    'text_secondary': (107, 114, 128),     # Gray text
    'text_white': (255, 255, 255),        # White text
    'accent': (147, 51, 234),             # Purple accent
    'accent_hover': (126, 34, 206),       # Darker purple
    'success': (34, 197, 94),             # Green
    'success_hover': (22, 163, 74),       # Darker green
    'shadow': (0, 0, 0, 50),              # Semi-transparent shadow
    'gradient_start': (147, 51, 234),     # Purple
    'gradient_end': (59, 130, 246),       # Blue
}

# Animation states
class FlipState(Enum):
    IDLE = 0
    FLIPPING_TO_BACK = 1
    FLIPPING_TO_FRONT = 2

# Enhanced fonts
try:
    font_title = pygame.font.Font(None, 56)
    font_large = pygame.font.Font(None, 44)
    font_medium = pygame.font.Font(None, 36)
    font_small = pygame.font.Font(None, 28)
    font_tiny = pygame.font.Font(None, 22)
except:
    # Fallback to default fonts
    font_title = pygame.font.Font(None, 56)
    font_large = pygame.font.Font(None, 44)
    font_medium = pygame.font.Font(None, 36)
    font_small = pygame.font.Font(None, 28)
    font_tiny = pygame.font.Font(None, 22)

class QuestionLoader:
    def __init__(self, json_file):
        self.json_file = json_file
        self.questions = []
        self.load_questions()
    
    def load_questions(self):
        """Load questions from JSON file"""
        try:
            with open(self.json_file, 'r', encoding='utf-8') as file:
                data = json.load(file)
                self.questions = data.get('questions', [])
                
        except FileNotFoundError:
            print(f"Error: Could not find file {self.json_file}")
            sys.exit(1)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON file: {e}")
            sys.exit(1)
        except Exception as e:
            print(f"Error loading questions: {e}")
            sys.exit(1)

class AnimatedFlashcard:
    def __init__(self, question, answer):
        self.question = question
        self.answer = answer
        self.showing_answer = False
        self.flip_state = FlipState.IDLE
        self.flip_progress = 0.0
        self.flip_speed = 8.0
        
    def start_flip(self):
        """Start the flip animation"""
        if self.flip_state == FlipState.IDLE:
            if self.showing_answer:
                self.flip_state = FlipState.FLIPPING_TO_FRONT
            else:
                self.flip_state = FlipState.FLIPPING_TO_BACK
            self.flip_progress = 0.0
    
    def update_animation(self, dt):
        """Update flip animation"""
        if self.flip_state != FlipState.IDLE:
            self.flip_progress += self.flip_speed * dt
            
            if self.flip_progress >= 1.0:
                self.flip_progress = 1.0
                self.showing_answer = not self.showing_answer
                self.flip_state = FlipState.IDLE
    
    def get_current_text(self):
        return self.answer if self.showing_answer else self.question
    
    def get_scale_x(self):
        """Get horizontal scale for flip animation"""
        if self.flip_state == FlipState.IDLE:
            return 1.0
        
        # Create a smooth flip effect
        progress = self.flip_progress
        if progress < 0.5:
            return 1.0 - (progress * 2.0)
        else:
            return (progress - 0.5) * 2.0
    
    def should_show_back(self):
        """Determine if we should show the back side during animation"""
        return self.flip_progress > 0.5

class ModernButton:
    def __init__(self, x, y, width, height, text, color, hover_color, text_color=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color or COLORS['text_white']
        self.is_hovered = False
        self.is_pressed = False
        
    def update(self, mouse_pos, mouse_pressed):
        self.is_hovered = self.rect.collidepoint(mouse_pos)
        self.is_pressed = self.is_hovered and mouse_pressed
        
    def draw(self, screen):
        current_color = self.hover_color if self.is_hovered else self.color
        
        # Draw shadow
        shadow_rect = self.rect.copy()
        shadow_rect.y += 4
        pygame.draw.rect(screen, (0, 0, 0, 30), shadow_rect, border_radius=12)
        
        # Draw button
        if self.is_pressed:
            button_rect = self.rect.copy()
            button_rect.y += 2
        else:
            button_rect = self.rect
            
        pygame.draw.rect(screen, current_color, button_rect, border_radius=12)
        
        # Draw text
        text_surface = font_medium.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=button_rect.center)
        screen.blit(text_surface, text_rect)

class FlashcardApp:
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("SE Forms Questions - Modern Flashcards")
        self.clock = pygame.time.Clock()
        
        # Load questions
        self.loader = QuestionLoader('questions.json')
        if not self.loader.questions:
            print("No questions found in the JSON file!")
            sys.exit(1)
        
        # Create flashcards
        self.flashcards = [AnimatedFlashcard(q['question'], q['answer']) for q in self.loader.questions]
        random.shuffle(self.flashcards)
        
        self.current_index = 0
        self.current_card = self.flashcards[self.current_index] if self.flashcards else None
        
        # UI elements
        self.card_rect = pygame.Rect(150, 150, SCREEN_WIDTH - 300, SCREEN_HEIGHT - 350)
        
        # Modern buttons
        button_y = SCREEN_HEIGHT - 120
        self.prev_button = ModernButton(50, button_y, 120, 50, "Previous", 
                                       COLORS['accent'], COLORS['accent_hover'])
        self.next_button = ModernButton(SCREEN_WIDTH - 170, button_y, 120, 50, "Next", 
                                       COLORS['accent'], COLORS['accent_hover'])
        self.shuffle_button = ModernButton(SCREEN_WIDTH // 2 - 60, button_y, 120, 50, "Shuffle", 
                                         COLORS['success'], COLORS['success_hover'])
        
        self.mouse_pos = (0, 0)
        self.mouse_pressed = False
        
    def create_gradient_surface(self, width, height, color1, color2, vertical=True):
        """Create a gradient surface"""
        gradient = pygame.Surface((width, height))
        if vertical:
            for y in range(height):
                ratio = y / height
                r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
                pygame.draw.line(gradient, (r, g, b), (0, y), (width, y))
        else:
            for x in range(width):
                ratio = x / width
                r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
                g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
                b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
                pygame.draw.line(gradient, (r, g, b), (x, 0), (x, height))
        return gradient
    
    def format_text(self, text):
        """Format text by processing markdown-style elements"""
        # Split by line breaks first
        paragraphs = text.split('\n')
        formatted_lines = []
        
        for paragraph in paragraphs:
            if not paragraph.strip():
                formatted_lines.append(("empty", ""))  # Empty line
                continue
                
            # Clean up the paragraph by removing markdown bold syntax
            clean_paragraph = paragraph.replace('**', '')
            
            # Handle bullet points
            if clean_paragraph.strip().startswith('•'):
                formatted_lines.append(('bullet', clean_paragraph.strip()))
            # Handle quotes
            elif clean_paragraph.strip().startswith('"') and clean_paragraph.strip().endswith('"'):
                formatted_lines.append(('quote', clean_paragraph.strip()))
            # Check if original had bold markers (before cleaning)
            elif '**' in paragraph:
                formatted_lines.append(('bold', clean_paragraph.strip()))
            else:
                formatted_lines.append(('normal', clean_paragraph.strip()))
        
        return formatted_lines
    
    def wrap_formatted_text(self, formatted_lines, base_font, max_width):
        """Wrap formatted text, handling different styles"""
        wrapped_lines = []
        
        for line_type, text in formatted_lines:
            if not text:
                wrapped_lines.append(('empty', ''))
                continue
                
            # Choose font based on type
            if line_type == 'bold':
                font = font_medium
            elif line_type == 'bullet':
                font = base_font
            elif line_type == 'quote':
                font = base_font
            else:
                font = base_font
            
            # Wrap the text
            if line_type == 'bullet':
                # Handle bullet points specially - preserve bullet and indent
                bullet_text = text[1:].strip()  # Remove bullet
                words = bullet_text.split(' ')
                current_line = "• "
                
                for word in words:
                    test_line = current_line + word + " "
                    if font.size(test_line)[0] <= max_width:
                        current_line = test_line
                    else:
                        if current_line.strip() != "•":
                            wrapped_lines.append((line_type, current_line.strip()))
                        current_line = "  " + word + " "  # Indent continuation
                
                if current_line.strip():
                    wrapped_lines.append((line_type, current_line.strip()))
                    
            else:
                # Normal wrapping
                words = text.split(' ')
                current_line = ""
                
                for word in words:
                    test_line = current_line + word + " "
                    if font.size(test_line)[0] <= max_width:
                        current_line = test_line
                    else:
                        if current_line:
                            wrapped_lines.append((line_type, current_line.strip()))
                        current_line = word + " "
                
                if current_line:
                    wrapped_lines.append((line_type, current_line.strip()))
        
        return wrapped_lines
    
    def draw_card(self):
        """Draw the animated flashcard"""
        if not self.current_card:
            return
        
        scale_x = self.current_card.get_scale_x()
        
        # Calculate card dimensions with scaling
        card_width = int(self.card_rect.width * scale_x)
        card_height = self.card_rect.height
        card_x = self.card_rect.centerx - card_width // 2
        card_y = self.card_rect.y
        
        if card_width <= 0:
            return
        
        scaled_rect = pygame.Rect(card_x, card_y, card_width, card_height)
        
        # Determine card colors based on state
        if self.current_card.flip_state == FlipState.IDLE:
            if self.current_card.showing_answer:
                card_color = COLORS['card_back']
                text_color = COLORS['text_white']
                badge_text = "ANSWER"
                badge_color = COLORS['success']
            else:
                card_color = COLORS['card_front']
                text_color = COLORS['text_primary']
                badge_text = "QUESTION"
                badge_color = COLORS['accent']
        else:
            # During animation, show appropriate side
            if self.current_card.should_show_back():
                card_color = COLORS['card_back']
                text_color = COLORS['text_white']
                badge_text = "ANSWER"
                badge_color = COLORS['success']
            else:
                card_color = COLORS['card_front']
                text_color = COLORS['text_primary']
                badge_text = "QUESTION"
                badge_color = COLORS['accent']
        
        # Draw card shadow
        shadow_rect = scaled_rect.copy()
        shadow_rect.y += 8
        shadow_rect.x += 4
        shadow_surface = pygame.Surface((shadow_rect.width, shadow_rect.height), pygame.SRCALPHA)
        pygame.draw.rect(shadow_surface, (0, 0, 0, 30), shadow_surface.get_rect(), border_radius=24)
        self.screen.blit(shadow_surface, shadow_rect)
        
        # Draw card background
        pygame.draw.rect(self.screen, card_color, scaled_rect, border_radius=24)
        
        # Draw subtle border
        border_color = COLORS['text_secondary'] if not self.current_card.showing_answer else (255, 255, 255, 50)
        pygame.draw.rect(self.screen, border_color, scaled_rect, width=2, border_radius=24)
        
        # Draw content only if card is visible enough
        if scale_x > 0.1:
            # Draw badge
            badge_rect = pygame.Rect(scaled_rect.right - 100, scaled_rect.top + 20, 80, 30)
            pygame.draw.rect(self.screen, badge_color, badge_rect, border_radius=15)
            badge_surface = font_tiny.render(badge_text, True, COLORS['text_white'])
            badge_text_rect = badge_surface.get_rect(center=badge_rect.center)
            self.screen.blit(badge_surface, badge_text_rect)
            
            # Draw card content with formatting
            text = self.current_card.get_current_text()
            
            # Choose base font size based on text length
            if len(text) < 150:
                base_font = font_medium
            elif len(text) < 400:
                base_font = font_small
            else:
                base_font = font_tiny
            
            content_width = scaled_rect.width - 60
            
            # Format and wrap text
            formatted_lines = self.format_text(text)
            wrapped_lines = self.wrap_formatted_text(formatted_lines, base_font, content_width)
            
            # Calculate spacing
            base_line_height = base_font.get_height() + 4
            
            # Calculate available space for text
            available_height = scaled_rect.height - 120
            max_lines = int(available_height / base_line_height)
            
            # Truncate if necessary
            display_lines = wrapped_lines[:max_lines] if len(wrapped_lines) > max_lines else wrapped_lines
            truncated = len(wrapped_lines) > max_lines
            
            # Calculate total height for centering
            total_height = len(display_lines) * base_line_height
            start_y = scaled_rect.y + 60 + (available_height - total_height) // 2
            
            # Render each formatted line
            for i, (line_type, line_text) in enumerate(display_lines):
                if line_type == 'empty':
                    continue
                    
                # Choose font and color based on line type
                if line_type == 'bold':
                    current_font = font_medium
                    current_color = text_color
                elif line_type == 'quote':
                    current_font = base_font
                    # Make quotes slightly lighter
                    if self.current_card.showing_answer:
                        current_color = (200, 200, 200)
                    else:
                        current_color = (80, 80, 80)
                elif line_type == 'bullet':
                    current_font = base_font
                    current_color = text_color
                else:
                    current_font = base_font
                    current_color = text_color
                
                # Render the text
                text_surface = current_font.render(line_text, True, current_color)
                text_rect = text_surface.get_rect()
                
                # Center normal text, left-align bullets
                if line_type == 'bullet':
                    text_rect.left = scaled_rect.left + 40
                else:
                    text_rect.centerx = scaled_rect.centerx
                    
                text_rect.y = start_y + i * base_line_height
                
                # Scale text horizontally to match card scaling
                if scale_x < 1.0:
                    scaled_width = int(text_surface.get_width() * scale_x)
                    if scaled_width > 0:
                        scaled_text = pygame.transform.scale(text_surface, (scaled_width, text_surface.get_height()))
                        scaled_text_rect = scaled_text.get_rect()
                        if line_type == 'bullet':
                            scaled_text_rect.left = text_rect.left
                        else:
                            scaled_text_rect.centerx = scaled_rect.centerx
                        scaled_text_rect.y = text_rect.y
                        self.screen.blit(scaled_text, scaled_text_rect)
                else:
                    self.screen.blit(text_surface, text_rect)
            
            # Show "..." if text was truncated
            if truncated and scale_x > 0.1:
                dots_surface = base_font.render("...", True, text_color)
                dots_rect = dots_surface.get_rect()
                dots_rect.centerx = scaled_rect.centerx
                dots_rect.y = start_y + len(display_lines) * base_line_height
                self.screen.blit(dots_surface, dots_rect)
            
            # Draw instruction text
            if self.current_card.flip_state == FlipState.IDLE:
                if not self.current_card.showing_answer:
                    instruction = "Click to reveal answer"
                else:
                    instruction = "Click to show question"
                
                instruction_surface = font_tiny.render(instruction, True, 
                                                     COLORS['text_secondary'] if not self.current_card.showing_answer else (255, 255, 255, 150))
                instruction_rect = instruction_surface.get_rect()
                instruction_rect.centerx = scaled_rect.centerx
                instruction_rect.bottom = scaled_rect.bottom - 20
                self.screen.blit(instruction_surface, instruction_rect)
    
    def draw_background(self):
        """Draw the modern gradient background"""
        gradient = self.create_gradient_surface(SCREEN_WIDTH, SCREEN_HEIGHT, 
                                              COLORS['bg_primary'], COLORS['bg_secondary'])
        self.screen.blit(gradient, (0, 0))
        
        # Add some subtle pattern
        for i in range(0, SCREEN_WIDTH, 100):
            for j in range(0, SCREEN_HEIGHT, 100):
                alpha = 20
                color = (*COLORS['accent'], alpha)
                circle_surface = pygame.Surface((20, 20), pygame.SRCALPHA)
                pygame.draw.circle(circle_surface, color, (10, 10), 8)
                self.screen.blit(circle_surface, (i, j))
    
    def draw_header(self):
        """Draw the modern header"""
        # Title
        title = "SE Forms Questions"
        title_surface = font_title.render(title, True, COLORS['text_white'])
        title_rect = title_surface.get_rect()
        title_rect.centerx = SCREEN_WIDTH // 2
        title_rect.y = 30
        self.screen.blit(title_surface, title_rect)
        
        # Subtitle
        subtitle = "Interactive Study Cards"
        subtitle_surface = font_medium.render(subtitle, True, COLORS['text_secondary'])
        subtitle_rect = subtitle_surface.get_rect()
        subtitle_rect.centerx = SCREEN_WIDTH // 2
        subtitle_rect.y = 75
        self.screen.blit(subtitle_surface, subtitle_rect)
        
        # Progress indicator
        if self.flashcards:
            progress_text = f"{self.current_index + 1} / {len(self.flashcards)}"
            progress_surface = font_large.render(progress_text, True, COLORS['accent'])
            progress_rect = progress_surface.get_rect()
            progress_rect.centerx = SCREEN_WIDTH // 2
            progress_rect.y = 105
            self.screen.blit(progress_surface, progress_rect)
            
            # Progress bar
            bar_width = 300
            bar_height = 6
            bar_x = SCREEN_WIDTH // 2 - bar_width // 2
            bar_y = 140
            
            # Background bar
            pygame.draw.rect(self.screen, COLORS['bg_secondary'], 
                           (bar_x, bar_y, bar_width, bar_height), border_radius=3)
            
            # Progress bar
            progress = (self.current_index + 1) / len(self.flashcards)
            progress_width = int(bar_width * progress)
            if progress_width > 0:
                gradient_bar = self.create_gradient_surface(progress_width, bar_height, 
                                                          COLORS['gradient_start'], COLORS['gradient_end'], False)
                self.screen.blit(gradient_bar, (bar_x, bar_y))
    
    def next_card(self):
        """Go to next card"""
        if self.current_index < len(self.flashcards) - 1:
            self.current_index += 1
            self.current_card = self.flashcards[self.current_index]
            self.current_card.showing_answer = False
            self.current_card.flip_state = FlipState.IDLE
    
    def prev_card(self):
        """Go to previous card"""
        if self.current_index > 0:
            self.current_index -= 1
            self.current_card = self.flashcards[self.current_index]
            self.current_card.showing_answer = False
            self.current_card.flip_state = FlipState.IDLE
    
    def shuffle_cards(self):
        """Shuffle the cards"""
        random.shuffle(self.flashcards)
        self.current_index = 0
        self.current_card = self.flashcards[self.current_index]
        self.current_card.showing_answer = False
        self.current_card.flip_state = FlipState.IDLE
    
    def handle_click(self, pos):
        """Handle mouse clicks"""
        if self.card_rect.collidepoint(pos) and self.current_card:
            if self.current_card.flip_state == FlipState.IDLE:
                self.current_card.start_flip()
        elif self.next_button.rect.collidepoint(pos):
            if self.current_index < len(self.flashcards) - 1:
                self.next_card()
        elif self.prev_button.rect.collidepoint(pos):
            if self.current_index > 0:
                self.prev_card()
        elif self.shuffle_button.rect.collidepoint(pos):
            self.shuffle_cards()
    
    def run(self):
        """Main game loop"""
        running = True
        last_time = pygame.time.get_ticks()
        
        while running:
            current_time = pygame.time.get_ticks()
            dt = (current_time - last_time) / 1000.0
            last_time = current_time
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        self.handle_click(event.pos)
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        if self.current_card and self.current_card.flip_state == FlipState.IDLE:
                            self.current_card.start_flip()
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_n:
                        self.next_card()
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_p:
                        self.prev_card()
                    elif event.key == pygame.K_s:
                        self.shuffle_cards()
            
            # Update
            self.mouse_pos = pygame.mouse.get_pos()
            self.mouse_pressed = pygame.mouse.get_pressed()[0]
            
            # Update buttons
            self.prev_button.update(self.mouse_pos, self.mouse_pressed)
            self.next_button.update(self.mouse_pos, self.mouse_pressed)
            self.shuffle_button.update(self.mouse_pos, self.mouse_pressed)
            
            # Update current card animation
            if self.current_card:
                self.current_card.update_animation(dt)
            
            # Draw everything
            self.draw_background()
            self.draw_header()
            self.draw_card()
            
            # Draw buttons
            self.prev_button.draw(self.screen)
            self.next_button.draw(self.screen)
            self.shuffle_button.draw(self.screen)
            
            pygame.display.flip()
            self.clock.tick(FPS)
        
        pygame.quit()

if __name__ == "__main__":
    app = FlashcardApp()
    app.run() 