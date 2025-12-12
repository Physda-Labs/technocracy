/**
 * Character class for the simulation
 */

import type { Character as CharacterData } from '@/src/types/character';
import {
  CHARACTER_CONFIG,
  WORLD_CONFIG,
  SPEECH_CONFIG,
  Direction,
  CharacterState,
  getRandomResponse,
} from './world';
import { drawSprite, drawShadow, drawSpeechBubble } from './canvas-utils';

export class SimulationCharacter {
  // Identity
  id: string;
  data: CharacterData;

  // Position and movement
  x: number;
  y: number;
  vx: number;
  vy: number;

  // Animation
  frameIndex: number = 0;
  row: Direction = Direction.DOWN;
  tickCount: number = 0;

  // State
  state: CharacterState = CharacterState.WANDERING;
  speechText: string = '';
  speechTimer: number = 0;
  speechBubbleHidden: boolean = false; // Toggle to hide/show speech bubble
  pendingSpeechTimeout: NodeJS.Timeout | null = null;

  // Sprite images
  image: HTMLImageElement | null = null;
  imageLoaded: boolean = false;
  sitImage: HTMLImageElement | null = null;
  sitImageLoaded: boolean = false;

  // Saved velocity when sitting
  savedVx: number = 0;
  savedVy: number = 0;

  constructor(characterData: CharacterData, x: number, y: number, vx: number, vy: number) {
    this.id = characterData.id.toString();
    this.data = characterData;
    this.x = x;
    this.y = y;
    this.vx = vx;
    this.vy = vy;

    // Load sprite image
    this.loadImage();
  }

  /**
   * Load the character's walk sprite
   */
  private loadImage(): void {
    this.image = new Image();

    // Allow cross-origin if needed
    this.image.crossOrigin = 'anonymous';

    this.image.onload = () => {
      this.imageLoaded = true;
    };

    this.image.onerror = (error) => {
      console.error(`Failed to load sprite for character ${this.id}:`, this.data.sprites.walk.url, error);
      this.imageLoaded = false;
    };

    // Use the walk sprite from the character data
    this.image.src = this.data.sprites.walk.url;

    // Load sit sprite
    this.loadSitImage();
  }

  /**
   * Load the character's sit sprite
   */
  private loadSitImage(): void {
    this.sitImage = new Image();
    this.sitImage.crossOrigin = 'anonymous';

    this.sitImage.onload = () => {
      this.sitImageLoaded = true;
    };

    this.sitImage.onerror = (error) => {
      console.error(`Failed to load sit sprite for character ${this.id}:`, error);
      this.sitImageLoaded = false;
    };

    // Use the sit sprite from the character data
    if (this.data.sprites.sit?.url) {
      this.sitImage.src = this.data.sprites.sit.url;
    }
  }

  /**
   * Update character position and state
   */
  update(deltaTime: number = 1, allCharacters: SimulationCharacter[] = []): void {
    // Update speech timer (independent of movement state)
    if (this.speechTimer > 0) {
      this.speechTimer -= deltaTime * 16.67; // Approximate ms per frame at 60fps
      if (this.speechTimer <= 0) {
        this.speechText = '';
        // Only return to wandering if we were talking (not sitting)
        if (this.state === CharacterState.TALKING) {
          this.state = CharacterState.WANDERING;
        }
      }
    }

    // Move character
    this.move();

    // Handle collisions if other characters are provided
    if (allCharacters.length > 0) {
      this.handleCollisions(allCharacters);
    }

    // Update animation
    this.updateAnimation();
  }

  /**
   * Move the character and handle world boundaries
   */
  private move(): void {
    // Don't move if sitting
    if (this.state === CharacterState.SITTING) {
      return;
    }

    // Update position
    this.x += this.vx;
    this.y += this.vy;

    // Bounce off world boundaries
    if (this.x < 0 || this.x > WORLD_CONFIG.WIDTH) {
      this.vx *= -1;
      this.x = Math.max(0, Math.min(WORLD_CONFIG.WIDTH, this.x));
    }
    if (this.y < 0 || this.y > WORLD_CONFIG.HEIGHT) {
      this.vy *= -1;
      this.y = Math.max(0, Math.min(WORLD_CONFIG.HEIGHT, this.y));
    }

    // Randomly change direction
    if (Math.random() < CHARACTER_CONFIG.DIRECTION_CHANGE_CHANCE) {
      const angle = Math.random() * Math.PI * 2;
      this.vx = Math.cos(angle) * CHARACTER_CONFIG.SPEED;
      this.vy = Math.sin(angle) * CHARACTER_CONFIG.SPEED;
    }
  }

  /**
   * Handle collisions with other characters
   */
  private handleCollisions(others: SimulationCharacter[]): void {
    for (const other of others) {
      if (other.id === this.id) continue;

      const dx = other.x - this.x;
      const dy = other.y - this.y;
      const distance = Math.sqrt(dx * dx + dy * dy);
      const minDistance = CHARACTER_CONFIG.HITBOX_RADIUS * 2;

      if (distance < minDistance) {
        // Collision detected: Push apart
        const angle = Math.atan2(dy, dx);

        const targetX = this.x + Math.cos(angle) * minDistance;
        const targetY = this.y + Math.sin(angle) * minDistance;

        const ax = (targetX - other.x) * 0.05;
        const ay = (targetY - other.y) * 0.05;

        this.vx -= ax;
        this.vy -= ay;
        other.vx += ax;
        other.vy += ay;
      }
    }
  }

  /**
   * Update animation frame based on movement direction
   */
  private updateAnimation(): void {
    // Determine direction based on velocity
    const absVx = Math.abs(this.vx);
    const absVy = Math.abs(this.vy);

    if (absVx > absVy) {
      // Moving more horizontally
      this.row = this.vx > 0 ? Direction.RIGHT : Direction.LEFT;
    } else {
      // Moving more vertically
      this.row = this.vy > 0 ? Direction.DOWN : Direction.UP;
    }

    // Cycle through frames
    this.tickCount += CHARACTER_CONFIG.ANIMATION_SPEED;
    if (this.tickCount >= 1) {
      this.tickCount = 0;
      this.frameIndex = (this.frameIndex + 1) % 9;
    }
  }

  /**
   * Make the character say something
   */
  ask(question: string): void {
    // Clear any pending speech
    if (this.pendingSpeechTimeout) {
      clearTimeout(this.pendingSpeechTimeout);
      this.pendingSpeechTimeout = null;
    }

    // Set speech text and timer
    this.speechText = getRandomResponse();
    this.speechTimer = SPEECH_CONFIG.DURATION_MS;

    // Only change state to TALKING if not sitting
    if (this.state !== CharacterState.SITTING) {
      this.state = CharacterState.TALKING;
    }
  }

  /**
   * Toggle sitting state - right click to sit/stand
   */
  toggleSit(): void {
    if (this.state === CharacterState.SITTING) {
      // Stand up - restore velocity
      this.state = CharacterState.WANDERING;
      this.vx = this.savedVx;
      this.vy = this.savedVy;
    } else {
      // Sit down - save velocity and stop
      this.savedVx = this.vx;
      this.savedVy = this.vy;
      this.vx = 0;
      this.vy = 0;
      this.state = CharacterState.SITTING;
    }
  }

  /**
   * Toggle the speech bubble visibility
   */
  toggleSpeechBubble(): void {
    this.speechBubbleHidden = !this.speechBubbleHidden;
  }

  /**
   * Draw the character on the canvas
   */
  draw(ctx: CanvasRenderingContext2D): void {
    const currentW = CHARACTER_CONFIG.WIDTH;
    const currentH = CHARACTER_CONFIG.HEIGHT;

    // Don't draw anything if sprite isn't loaded
    if (!this.imageLoaded || !this.image || !this.image.complete || this.image.naturalWidth === 0) {
      return;
    }

    ctx.save();

    // Draw hitbox visualization (for debugging)
    ctx.strokeStyle = 'rgba(0, 255, 0, 0.3)';
    ctx.lineWidth = 1;
    ctx.setLineDash([5, 5]); // Dotted line pattern
    ctx.beginPath();
    ctx.arc(this.x, this.y, CHARACTER_CONFIG.HITBOX_RADIUS, 0, Math.PI * 2);
    ctx.stroke();
    ctx.setLineDash([]); // Reset line dash

    // Draw interaction radius (red dotted circle)
    ctx.strokeStyle = 'rgba(163, 45, 45, 0.5)';
    ctx.lineWidth = 1;
    ctx.setLineDash([5, 5]); // Dotted line pattern
    ctx.beginPath();
    ctx.arc(this.x, this.y, CHARACTER_CONFIG.INTERACTION_RADIUS, 0, Math.PI * 2);
    ctx.stroke();
    ctx.setLineDash([]); // Reset line dash

    // Draw shadow
    drawShadow(ctx, this.x, this.y, currentW);

    // Draw sprite based on state
    try {
      if (this.state === CharacterState.SITTING && this.sitImageLoaded && this.sitImage) {
        // Draw sitting sprite - use specific frame (row 2, col 2 in 0-indexed = facing screen)
        // Sit sprite is 3 columns x 4 rows
        const sitFrameW = this.sitImage.width / 3;
        const sitFrameH = this.sitImage.height / 4;
        const sitCol = 1; // Column 3 (0-indexed = 2)
        const sitRow = 2; // Row 3 (0-indexed = 2)

        ctx.drawImage(
          this.sitImage,
          sitCol * sitFrameW, sitRow * sitFrameH, sitFrameW, sitFrameH,
          this.x - currentW / 2, this.y - currentH / 2, currentW, currentH
        );
      } else {
        // Draw walk sprite
        drawSprite(
          ctx,
          this.image,
          this.frameIndex,
          this.row,
          this.x,
          this.y,
          currentW,
          currentH
        );
      }
    } catch (error) {
      // Silently fail if sprite drawing fails
      console.error('Error drawing sprite:', error);
    }

    // Draw speech bubble if has speech text and not hidden (independent of movement state)
    if (this.speechText && !this.speechBubbleHidden) {
      drawSpeechBubble(ctx, this.x, this.y - currentH / 2, this.speechText, 12);
    }

    ctx.restore();
  }

  /**
   * Cleanup method to clear timeouts
   */
  cleanup(): void {
    if (this.pendingSpeechTimeout) {
      clearTimeout(this.pendingSpeechTimeout);
      this.pendingSpeechTimeout = null;
    }
  }
}
