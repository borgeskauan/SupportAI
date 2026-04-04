import { Component, computed, inject, signal } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { toObservable } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { finalize, switchMap } from 'rxjs';
import { FaqDataService } from '../data-access/faq-data.service';
import { DraftStatus, FaqDraft, localizeDraftStatus } from '../data-access/faq.models';

@Component({
  selector: 'app-faq-drafts-list',
  imports: [RouterLink],
  templateUrl: './faq-drafts-list.component.html',
  styleUrl: './faq-drafts-list.component.css'
})
export class FaqDraftsListComponent {
  private readonly faqData = inject(FaqDataService);
  private noticeTimer: ReturnType<typeof setTimeout> | null = null;

  protected readonly isRegenerating = signal(false);
  protected readonly regenerationNotice = signal('');

  /**
   * Refresh trigger signal.
   * Increment this to trigger a new fetch of the FAQ list.
   */
  private readonly refreshTrigger = signal(0);

  /**
   * Drafts signal that re-fetches whenever refreshTrigger changes.
   */
  protected readonly drafts = toSignal(
    toObservable(this.refreshTrigger).pipe(
      switchMap(() => this.faqData.getFaqDrafts())
    ),
    {
      initialValue: [] as FaqDraft[]
    }
  );

  protected readonly averageConfidence = computed(() => {
    const items = this.drafts();
    if (!items.length) {
      return 0;
    }

    const total = items.reduce((sum, draft) => sum + draft.confidence, 0);
    const avg = (total / items.length) * 100; // Convert from 0-1 to 0-100
    return Math.round(avg);
  });

  /**
   * Format confidence score from 0-1 decimal range to 0-100 percentage
   */
  protected formatConfidence(score: number): number {
    return Math.round(score * 100);
  }

  protected statusLabel(status: DraftStatus): string {
    return localizeDraftStatus(status);
  }

  protected regenerate(): void {
    if (this.isRegenerating()) {
      return;
    }

    this.isRegenerating.set(true);
    const startedAt = Date.now();

    this.faqData
      .regenerateFaqDrafts()
      .pipe(
        finalize(() => {
          const elapsedMs = Date.now() - startedAt;
          const minimumSpinnerMs = 900;
          const remainingMs = Math.max(0, minimumSpinnerMs - elapsedMs);

          setTimeout(() => {
            this.isRegenerating.set(false);
          }, remainingMs);
        })
      )
      .subscribe({
        next: () => {
          // Trigger a refresh of the FAQ list
          this.refreshTrigger.update((v) => v + 1);
          this.showNotice($localize`:@@drafts_regenerated_successfully:Drafts regenerated successfully.`);
        },
        error: () => {
          this.showNotice($localize`:@@drafts_regeneration_failed:Regeneration failed. Please try again.`);
        }
      });
  }

  private showNotice(message: string): void {
    this.regenerationNotice.set(message);
    if (this.noticeTimer) {
      clearTimeout(this.noticeTimer);
    }

    this.noticeTimer = setTimeout(() => {
      this.regenerationNotice.set('');
    }, 2600);
  }
}
