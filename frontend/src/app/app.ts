import { Component, signal, effect } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { FaqDataService } from './data-access/faq-data.service';
import { ErrorOverlayComponent } from './error-overlay/error-overlay.component';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, ErrorOverlayComponent],
  templateUrl: './app.html',
  styleUrl: './app.css'
})
export class App {
  protected errorMessage = signal<string | null>(null);

  constructor(private faqData: FaqDataService) {
    // Load FAQs on app initialization and catch any errors
    effect(() => {
      this.faqData.getFaqDrafts().subscribe({
        next: () => {
          this.errorMessage.set(null);
        },
        error: (error: unknown) => {
          const message = error instanceof Error ? error.message : 'Unknown error';
          console.error('Failed to load FAQs:', message);
          this.errorMessage.set(
            'Unable to connect to the backend server. Please ensure the server is running and try refreshing the page.'
          );
        }
      });
    });
  }
}
