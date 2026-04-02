import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';

/**
 * ErrorOverlay Component
 * Displays a blocking error message overlay that covers the entire screen
 * Used when backend is unavailable or app initialization fails
 */
@Component({
  selector: 'app-error-overlay',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './error-overlay.component.html',
  styleUrls: ['./error-overlay.component.css'],
})
export class ErrorOverlayComponent {
  @Input() message: string = 'Backend service is unavailable. Please refresh the page.';
  readonly window = window;
}
