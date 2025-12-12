/**
 * Canvas component for rendering the character world
 */

'use client';

import { useRef, useEffect, forwardRef, useState } from 'react';
import type { Camera } from '@/src/hooks/useCamera';
import type { SimulationCharacter } from '@/src/lib/character';
import { WORLD_CONFIG, CHARACTER_CONFIG } from '@/src/lib/world';
import { drawGrid } from '@/src/lib/canvas-utils';

interface WorldCanvasProps {
  characters: SimulationCharacter[];
  camera: Camera;
  onWheel: (e: WheelEvent) => void;
  onMouseDown: (e: MouseEvent) => void;
  onMouseMove: (e: MouseEvent) => void;
  onMouseUp: () => void;
  isDragging: boolean;
}

export const WorldCanvas = forwardRef<HTMLCanvasElement, WorldCanvasProps>(
  function WorldCanvas(
    { characters, camera, onWheel, onMouseDown, onMouseMove, onMouseUp, isDragging },
    ref
  ) {
    const internalRef = useRef<HTMLCanvasElement>(null);
    const canvasRef = (ref as React.RefObject<HTMLCanvasElement>) || internalRef;

    // Track if hovering over a character's interaction radius
    const [isHoveringCharacter, setIsHoveringCharacter] = useState(false);

    // Use refs to access latest values without restarting render loop
    const charactersRef = useRef(characters);
    const cameraRef = useRef(camera);

    useEffect(() => {
      charactersRef.current = characters;
    }, [characters]);

    useEffect(() => {
      cameraRef.current = camera;
    }, [camera]);

    // Convert screen coordinates to world coordinates
    const screenToWorld = (screenX: number, screenY: number) => {
      const canvas = canvasRef.current;
      if (!canvas) return { x: 0, y: 0 };
      const currentCamera = cameraRef.current;
      const rect = canvas.getBoundingClientRect();
      const canvasX = screenX - rect.left;
      const canvasY = screenY - rect.top;
      // Reverse camera transformations
      const worldX = (canvasX - canvas.width / 2) / currentCamera.zoom + currentCamera.x;
      const worldY = (canvasY - canvas.height / 2) / currentCamera.zoom + currentCamera.y;
      return { x: worldX, y: worldY };
    };

    // Check if a point is within any character's interaction radius
    const isPointInCharacterRadius = (worldX: number, worldY: number): boolean => {
      for (const character of charactersRef.current) {
        const dx = worldX - character.x;
        const dy = worldY - character.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        if (distance <= CHARACTER_CONFIG.INTERACTION_RADIUS) {
          return true;
        }
      }
      return false;
    };

    // Get the character at a given world point (returns the closest one if overlapping)
    const getCharacterAtPoint = (worldX: number, worldY: number) => {
      let closestCharacter = null;
      let closestDistance: number = CHARACTER_CONFIG.INTERACTION_RADIUS;

      for (const character of charactersRef.current) {
        const dx = worldX - character.x;
        const dy = worldY - character.y;
        const distance = Math.sqrt(dx * dx + dy * dy);
        if (distance <= closestDistance) {
          closestDistance = distance;
          closestCharacter = character;
        }
      }
      return closestCharacter;
    };

    // Handle mouse move for hover detection
    const handleMouseMoveForHover = (e: MouseEvent) => {
      const { x, y } = screenToWorld(e.clientX, e.clientY);
      setIsHoveringCharacter(isPointInCharacterRadius(x, y));
    };

    // Track mouse position for click detection (to distinguish from drag)
    const mouseDownPos = useRef<{ x: number; y: number } | null>(null);

    // Handle click on character to toggle speech bubble
    const handleClick = (e: MouseEvent) => {
      // Only trigger if this was a click, not a drag
      if (mouseDownPos.current) {
        const dx = e.clientX - mouseDownPos.current.x;
        const dy = e.clientY - mouseDownPos.current.y;
        const dragDistance = Math.sqrt(dx * dx + dy * dy);

        // If dragged more than 5 pixels, it's a drag not a click
        if (dragDistance > 5) {
          mouseDownPos.current = null;
          return;
        }
      }

      const { x, y } = screenToWorld(e.clientX, e.clientY);
      const character = getCharacterAtPoint(x, y);
      if (character) {
        character.toggleSpeechBubble();
      }
      mouseDownPos.current = null;
    };

    const handleMouseDownForClick = (e: MouseEvent) => {
      mouseDownPos.current = { x: e.clientX, y: e.clientY };
    };

    // Setup canvas event listeners
    useEffect(() => {
      const canvas = canvasRef.current;
      if (!canvas) return;

      const combinedMouseMove = (e: MouseEvent) => {
        onMouseMove(e);
        handleMouseMoveForHover(e);
      };

      const combinedMouseDown = (e: MouseEvent) => {
        onMouseDown(e);
        handleMouseDownForClick(e);
      };

      const combinedMouseUp = (e: MouseEvent) => {
        handleClick(e);
        onMouseUp();
      };

      canvas.addEventListener('wheel', onWheel, { passive: false });
      canvas.addEventListener('mousedown', combinedMouseDown);
      canvas.addEventListener('mousemove', combinedMouseMove);
      canvas.addEventListener('mouseup', combinedMouseUp);
      canvas.addEventListener('mouseleave', onMouseUp);

      return () => {
        canvas.removeEventListener('wheel', onWheel);
        canvas.removeEventListener('mousedown', combinedMouseDown);
        canvas.removeEventListener('mousemove', combinedMouseMove);
        canvas.removeEventListener('mouseup', combinedMouseUp);
        canvas.removeEventListener('mouseleave', onMouseUp);
      };
    }, [canvasRef, onWheel, onMouseDown, onMouseMove, onMouseUp]);

    // Setup canvas and resize handling
    useEffect(() => {
      const canvas = canvasRef.current;
      if (!canvas) return;

      const resizeCanvas = () => {
        const { width, height } = canvas.getBoundingClientRect();
        canvas.width = width;
        canvas.height = height;
      };

      resizeCanvas();
      window.addEventListener('resize', resizeCanvas);

      return () => {
        window.removeEventListener('resize', resizeCanvas);
      };
    }, [canvasRef]);

    // Continuous render loop
    useEffect(() => {
      const canvas = canvasRef.current;
      if (!canvas) return;

      const ctx = canvas.getContext('2d');
      if (!ctx) return;

      let animationFrameId: number;

      const render = () => {
        const currentCamera = cameraRef.current;
        const currentCharacters = charactersRef.current;

        // Clear canvas completely
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.fillStyle = '#333333';
        ctx.fillRect(0, 0, canvas.width, canvas.height);

        // Set image smoothing for better sprite rendering
        ctx.imageSmoothingEnabled = true;
        ctx.imageSmoothingQuality = 'high';

        // Save context state
        ctx.save();

        // Apply camera transformations
        ctx.translate(canvas.width / 2, canvas.height / 2);
        ctx.scale(currentCamera.zoom, currentCamera.zoom);
        ctx.translate(-currentCamera.x, -currentCamera.y);

        // Draw world background
        ctx.fillStyle = '#2a2a2a';
        ctx.fillRect(0, 0, WORLD_CONFIG.WIDTH, WORLD_CONFIG.HEIGHT);

        // Draw grid
        drawGrid(ctx, WORLD_CONFIG.WIDTH, WORLD_CONFIG.HEIGHT);

        // Sort characters by Y position (painter's algorithm)
        const sortedCharacters = [...currentCharacters].sort((a, b) => a.y - b.y);

        // Draw all characters
        for (const character of sortedCharacters) {
          character.draw(ctx);
        }

        // Restore context state
        ctx.restore();

        // Continue the loop
        animationFrameId = requestAnimationFrame(render);
      };

      // Start the render loop
      animationFrameId = requestAnimationFrame(render);

      return () => {
        cancelAnimationFrame(animationFrameId);
      };
    }, [canvasRef]);

    return (
      <canvas
        ref={canvasRef}
        className={`w-full h-full ${isDragging ? 'cursor-grabbing' : isHoveringCharacter ? 'cursor-pointer' : 'cursor-grab'}`}
      />
    );
  }
);
