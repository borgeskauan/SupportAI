import { Component, inject, signal } from '@angular/core';
import { toSignal, toObservable } from '@angular/core/rxjs-interop';
import { ActivatedRoute, RouterLink } from '@angular/router';
import { combineLatest, map, switchMap } from 'rxjs';
import { FaqDataService } from '../data-access/faq-data.service';
import { DraftStatus } from '../data-access/faq.models';

@Component({
  selector: 'app-faq-detail',
  imports: [RouterLink],
  templateUrl: './faq-detail.component.html',
  styleUrl: './faq-detail.component.css'
})
export class FaqDetailComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly faqData = inject(FaqDataService);

  /**
   * Refresh trigger signal.
   * Increment this to trigger a re-fetch of the detail.
   */
  private readonly refreshTrigger = signal(0);

  /**
   * Detail observable that re-fetches when either route params or refreshTrigger changes.
   */
  protected readonly detail = toSignal(
    combineLatest([
      this.route.paramMap,
      toObservable(this.refreshTrigger)
    ]).pipe(
      map(([params]) => params.get('id') ?? '1'),
      switchMap((id) => this.faqData.getFaqDetailById(id))
    ),
    {
      initialValue: this.faqData.getFallbackDetail()
    }
  );

  protected approve(): void {
    this.updateStatus('Reviewed');
  }

  protected reject(): void {
    this.updateStatus('Rejected');
  }

  protected statusClass(status: DraftStatus): string {
    return status.toLowerCase();
  }

  /**
   * Format confidence score from 0-1 decimal range to 0-100 percentage
   */
  protected formatConfidence(score: number): number {
    return Math.round(score * 100);
  }

  private updateStatus(status: DraftStatus): void {
    this.faqData.updateFaqStatus(this.detail().id, status).subscribe(() => {
      // After status update completes, trigger a refresh to fetch the updated detail
      this.refreshTrigger.update((v) => v + 1);
    });
  }
}
