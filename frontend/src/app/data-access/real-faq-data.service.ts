import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, BehaviorSubject } from 'rxjs';
import { map } from 'rxjs/operators';

import { FaqDataService } from './faq-data.service';
import { API_ENDPOINTS } from './api-config';
import {
  FaqDraft,
  FaqDetail,
  FaqDetailUpdate,
  DraftStatus,
  BackendFaqDraft,
  BackendFaqListResponse,
  mapBackendToFaqDraft,
  mapBackendToFaqDetail,
} from './faq.models';

/**
 * RealFaqDataService
 * Fetches FAQ data from backend API while keeping edit/approve/reject state in-memory.
 * - GET /faqs: list all FAQs
 * - POST /faqs/generate: regenerate all FAQs
 * - Edits and status changes are ephemeral (in-memory only, no persistence)
 */
@Injectable()
export class RealFaqDataService implements FaqDataService {
  /**
   * In-memory store for edits and status overrides
   * Maps faq_id -> { status, content updates }
   */
  private overrides = new Map<
    string,
    {
      status?: DraftStatus;
      content?: Partial<FaqDetail>;
    }
  >();

  /**
   * Cached drafts from backend (always fetched fresh on startup)
   */
  private draftsCache$ = new BehaviorSubject<FaqDraft[]>([]);

  /**
   * Cached details map (keyed by faq_id)
   */
  private detailsCache = new Map<string, FaqDetail>();

  constructor(private http: HttpClient) {}

  /**
   * Get all FAQ drafts from backend
   */
  getFaqDrafts(): Observable<FaqDraft[]> {
    return this.http.get<BackendFaqListResponse>(API_ENDPOINTS.faqs).pipe(
      map((response) => {
        const drafts = response.faqs.map(mapBackendToFaqDraft);

        // Apply any cached edits/status changes
        const withOverrides = drafts.map((draft) => {
          const override = this.overrides.get(draft.id);
          if (override?.status) {
            return { ...draft, status: override.status };
          }
          return draft;
        });

        // Cache for detail lookups
        this.draftsCache$.next(withOverrides);
        return withOverrides;
      })
    );
  }

  /**
   * Get FAQ detail by ID
   * Falls back to cached drafts if not yet loaded
   */
  getFaqDetailById(id: string): Observable<FaqDetail> {
    // Check if we have it cached first
    if (this.detailsCache.has(id)) {
      const cached = this.detailsCache.get(id)!;
      const override = this.overrides.get(id);
      if (override?.status) {
        cached.status = override.status;
      }
      if (override?.content) {
        Object.assign(cached, override.content);
      }
      return new Observable((sub) => {
        sub.next(cached);
        sub.complete();
      });
    }

    // Otherwise fetch all drafts and find the one we want
    return this.http.get<BackendFaqListResponse>(API_ENDPOINTS.faqs).pipe(
      map((response) => {
        const backendDraft = response.faqs.find((f) => f.faq_id === id);
        if (!backendDraft) {
          throw new Error(`FAQ with id ${id} not found`);
        }

        const detail = mapBackendToFaqDetail(backendDraft);

        // Apply overrides
        const override = this.overrides.get(id);
        if (override?.status) {
          detail.status = override.status;
        }
        if (override?.content) {
          Object.assign(detail, override.content);
        }

        // Cache for future lookups
        this.detailsCache.set(id, detail);
        return detail;
      })
    );
  }

  /**
   * Update FAQ draft (frontend-only, in-memory)
   */
  updateFaqDraft(id: string, updates: FaqDetailUpdate): Observable<FaqDetail> {
    const current = this.detailsCache.get(id) || this.getFallbackDetail();
    const updated = { ...current, ...updates };

    // Store in overrides
    this.overrides.set(id, {
      status: this.overrides.get(id)?.status,
      content: updates,
    });

    // Update cache
    this.detailsCache.set(id, updated);

    return new Observable((sub) => {
      sub.next(updated);
      sub.complete();
    });
  }

  /**
   * Update FAQ status (frontend-only, in-memory)
   */
  updateFaqStatus(id: string, status: DraftStatus): Observable<FaqDetail> {
    const current = this.detailsCache.get(id) || this.getFallbackDetail();
    const updated = { ...current, status, reviewNeeded: false };

    // Store in overrides
    const existing = this.overrides.get(id) || {};
    this.overrides.set(id, {
      ...existing,
      status,
    });

    // Update cache
    this.detailsCache.set(id, updated);

    return new Observable((sub) => {
      sub.next(updated);
      sub.complete();
    });
  }

  /**
   * Regenerate all FAQs (fetches from backend, clears local overrides)
   */
  regenerateFaqDrafts(): Observable<FaqDraft[]> {
    return this.http.post<BackendFaqListResponse>(API_ENDPOINTS.generateFaqs, {}).pipe(
      map((response) => {
        // Clear all overrides when regenerating
        this.overrides.clear();
        this.detailsCache.clear();

        const drafts = response.faqs.map(mapBackendToFaqDraft);
        this.draftsCache$.next(drafts);
        return drafts;
      })
    );
  }

  /**
   * Fallback detail object (used when no data available)
   */
  getFallbackDetail(): FaqDetail {
    return {
      id: 'unknown',
      title: 'Unknown Draft',
      intent: '',
      family: '',
      status: 'Draft',
      confidence: 0,
      caseCount: 0,
      updated: new Date().toISOString(),
      reviewNeeded: false,
      problemStatement: '',
      causeExplanation: '',
      steps: [],
      edgeCases: [],
      contactSupport: '',
      evidence: [],
    };
  }
}
