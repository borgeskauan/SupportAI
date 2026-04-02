import { Component, computed, effect, inject } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { FormsModule } from '@angular/forms';
import { ActivatedRoute, Router, RouterLink } from '@angular/router';
import { map, switchMap } from 'rxjs';
import { FaqDataService } from '../data-access/faq-data.service';

@Component({
  selector: 'app-faq-edit',
  imports: [FormsModule, RouterLink],
  templateUrl: './faq-edit.component.html',
  styleUrl: './faq-edit.component.css'
})
export class FaqEditComponent {
  private readonly route = inject(ActivatedRoute);
  private readonly router = inject(Router);
  private readonly faqData = inject(FaqDataService);

  protected readonly detail = toSignal(
    this.route.paramMap.pipe(
      map((params) => params.get('id') ?? '1'),
      switchMap((id) => this.faqData.getFaqDetailById(id))
    ),
    {
      initialValue: this.faqData.getFallbackDetail()
    }
  );

  protected readonly detailId = computed(() => this.detail().id);

  protected title = '';
  protected intent = '';
  protected problemStatement = '';
  protected causeExplanation = '';
  protected stepsText = '';
  protected edgeCasesText = '';
  protected contactSupport = '';

  constructor() {
    effect(() => {
      const current = this.detail();
      this.title = current.title;
      this.intent = current.intent;
      this.problemStatement = current.problemStatement;
      this.causeExplanation = current.causeExplanation;
      this.stepsText = current.steps.join('\n');
      this.edgeCasesText = current.edgeCases.join('\n');
      this.contactSupport = current.contactSupport;
    });
  }

  protected save(): void {
    const id = this.detailId();

    this.faqData
      .updateFaqDraft(id, {
        title: this.title.trim(),
        intent: this.intent.trim(),
        problemStatement: this.problemStatement.trim(),
        causeExplanation: this.causeExplanation.trim(),
        steps: this.toLines(this.stepsText),
        edgeCases: this.toLines(this.edgeCasesText),
        contactSupport: this.contactSupport.trim()
      })
      .subscribe(() => {
        this.router.navigate(['/faq-drafts', id]);
      });
  }

  private toLines(value: string): string[] {
    return value
      .split('\n')
      .map((line) => line.trim())
      .filter((line) => line.length > 0);
  }
}
