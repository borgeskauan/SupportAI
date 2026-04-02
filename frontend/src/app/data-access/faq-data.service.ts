import { Observable } from 'rxjs';
import { DraftStatus, FaqDetail, FaqDetailUpdate, FaqDraft } from './faq.models';

export abstract class FaqDataService {
  abstract getFaqDrafts(): Observable<FaqDraft[]>;
  abstract getFaqDetailById(id: string): Observable<FaqDetail>;
  abstract regenerateFaqDrafts(): Observable<FaqDraft[]>;
  abstract updateFaqDraft(id: string, updates: FaqDetailUpdate): Observable<FaqDetail>;
  abstract updateFaqStatus(id: string, status: DraftStatus): Observable<FaqDetail>;
  abstract getFallbackDetail(): FaqDetail;
}
