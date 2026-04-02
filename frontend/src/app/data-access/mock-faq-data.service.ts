import { Injectable } from '@angular/core';
import { BehaviorSubject, Observable, map, of } from 'rxjs';
import { FaqDataService } from './faq-data.service';
import { DraftStatus, FaqDetail, FaqDetailUpdate, FaqDraft } from './faq.models';

interface FaqStore {
  drafts: FaqDraft[];
  detailsById: Record<string, FaqDetail>;
}

/**
 * MockFaqDataService
 * Provides in-memory FAQ store with seed data
 * Used for development/testing when backend is unavailable
 * Note: No localStorage persistence (all state is ephemeral)
 */
@Injectable()
export class MockFaqDataService implements FaqDataService {
  private readonly seedDrafts: FaqDraft[] = [
    {
      id: '1',
      title: 'Password reset email not received',
      intent: 'User cannot complete account recovery due to missing reset email',
      family: 'Authentication',
      status: 'Draft',
      confidence: 92,
      caseCount: 18,
      updated: '2h ago'
    },
    {
      id: '2',
      title: 'Duplicate charge confusion',
      intent: 'Handling pending authorization holds vs actual charges',
      family: 'Payments',
      status: 'Reviewed',
      confidence: 88,
      caseCount: 32,
      updated: '5h ago'
    },
    {
      id: '3',
      title: 'Why is the logo blue?',
      intent: 'Non-functional aesthetic queries',
      family: 'Branding',
      status: 'Rejected',
      confidence: 21,
      caseCount: 3,
      updated: '1d ago'
    },
    {
      id: '4',
      title: 'Reset password link expired',
      intent: 'Security policy regarding 24hr expiration',
      family: 'Security',
      status: 'Draft',
      confidence: 98,
      caseCount: 54,
      updated: '45m ago'
    },
    {
      id: '5',
      title: 'Unable to track refund status',
      intent: 'Clarifies refund timelines and tracking touchpoints',
      family: 'Refunds',
      status: 'Draft',
      confidence: 82,
      caseCount: 26,
      updated: '3h ago'
    },
    {
      id: '6',
      title: 'Delivery date changed after checkout',
      intent: 'Explains dispatch windows and ETA recalculation',
      family: 'Shipping',
      status: 'Reviewed',
      confidence: 91,
      caseCount: 47,
      updated: '6h ago'
    }
  ];

  private readonly seedDetailsById: Record<string, FaqDetail> = {
    '1': {
      id: '1',
      intent: 'User cannot complete account recovery due to missing reset email',
      updated: '2h ago',
      family: 'Authentication',
      status: 'Draft',
      reviewNeeded: true,
      title: 'Password reset email not received',
      confidence: 92,
      caseCount: 18,
      problemStatement:
        'Users report that after initiating password reset from the login page, the recovery email does not arrive in their inbox, which blocks access.',
      causeExplanation:
        'Most cases are caused by strict SMTP filters on corporate or education domains. Secondary causes include account-level blocklists and typographical errors in the registered email address.',
      steps: [
        'Check Spam, Junk, and Promotions folders first.',
        'Whitelist no-reply@system.knowledge.base in your mail client.',
        'Wait up to 10 minutes during peak traffic windows.',
        'Retry once only; repeated attempts can trigger temporary security lockouts.'
      ],
      edgeCases: [
        'Single sign-on accounts (Google or GitHub)',
        'Mailbox quota full and rejecting incoming emails',
        'Dormant accounts pending deletion policy'
      ],
      contactSupport:
        'Escalate to Tier 2 if no email arrives after 30 minutes and spam folders were verified. Include SMTP bounce/deferred codes in the handoff notes.',
      evidence: [
        {
          id: '#4920',
          source: 'Email',
          summary: 'Trying reset repeatedly since morning. Inbox and junk both empty.',
          timeAgo: '2 hours ago'
        },
        {
          id: '#4811',
          source: 'Chat',
          summary: 'User on EDU domain reports no delivery; SMTP shows deferred status.',
          timeAgo: '5 hours ago'
        },
        {
          id: '#4702',
          source: 'Email',
          summary: 'Forgot password flow does not trigger message for company-x.com account.',
          timeAgo: '1 day ago'
        }
      ]
    }
  };

  private readonly generationTemplates: Array<Pick<FaqDraft, 'title' | 'intent' | 'family' | 'caseCount'>> = [
    {
      title: 'Password reset email not received',
      intent: 'User cannot complete account recovery due to missing reset email',
      family: 'Authentication',
      caseCount: 18
    },
    {
      title: 'Duplicate charge confusion',
      intent: 'Clarifies authorization hold versus posted transaction',
      family: 'Payments',
      caseCount: 32
    },
    {
      title: 'Delivery date changed after checkout',
      intent: 'Explains ETA recalculation after warehouse processing',
      family: 'Shipping',
      caseCount: 47
    },
    {
      title: 'Refund tracking unavailable',
      intent: 'Shows how to track refund status and expected payout windows',
      family: 'Refunds',
      caseCount: 26
    },
    {
      title: '2FA code not accepted',
      intent: 'Troubleshoots time drift and backup code handling',
      family: 'Security',
      caseCount: 21
    },
    {
      title: 'Invoice download returns error',
      intent: 'Addresses PDF generation failures for archived invoices',
      family: 'Billing',
      caseCount: 13
    }
  ];

  private readonly store$ = new BehaviorSubject<FaqStore>({
    drafts: this.seedDrafts,
    detailsById: this.seedDetailsById,
  });

  getFaqDrafts(): Observable<FaqDraft[]> {
    return this.store$.pipe(map((store) => store.drafts));
  }

  getFaqDetailById(id: string): Observable<FaqDetail> {
    return this.store$.pipe(
      map((store) => store.detailsById[id] ?? this.getFallbackFromStore(store))
    );
  }

  regenerateFaqDrafts(): Observable<FaqDraft[]> {
    const regeneratedStore = this.buildGeneratedStore();
    this.store$.next(regeneratedStore);
    return of(regeneratedStore.drafts);
  }

  updateFaqDraft(id: string, updates: FaqDetailUpdate): Observable<FaqDetail> {
    const currentStore = this.store$.value;
    const currentDetail = currentStore.detailsById[id] ?? this.getFallbackFromStore(currentStore);
    const updatedDetail: FaqDetail = {
      ...currentDetail,
      ...updates,
      updated: 'Just now'
    };

    const updatedDrafts = currentStore.drafts.map((draft) => {
      if (draft.id !== id) {
        return draft;
      }

      return {
        ...draft,
        title: updatedDetail.title,
        intent: updatedDetail.intent,
        updated: updatedDetail.updated
      };
    });

    const nextStore: FaqStore = {
      drafts: updatedDrafts,
      detailsById: {
        ...currentStore.detailsById,
        [id]: updatedDetail
      }
    };

    this.store$.next(nextStore);
    return of(updatedDetail);
  }

  updateFaqStatus(id: string, status: DraftStatus): Observable<FaqDetail> {
    const currentStore = this.store$.value;
    const currentDetail = currentStore.detailsById[id] ?? this.getFallbackFromStore(currentStore);
    const updatedDetail: FaqDetail = {
      ...currentDetail,
      status,
      reviewNeeded: status === 'Draft',
      updated: 'Just now'
    };

    const updatedDrafts = currentStore.drafts.map((draft) => {
      if (draft.id !== id) {
        return draft;
      }

      return {
        ...draft,
        status,
        updated: updatedDetail.updated
      };
    });

    const nextStore: FaqStore = {
      drafts: updatedDrafts,
      detailsById: {
        ...currentStore.detailsById,
        [id]: updatedDetail
      }
    };

    this.store$.next(nextStore);
    return of(updatedDetail);
  }

  getFallbackDetail(): FaqDetail {
    return this.getFallbackFromStore(this.store$.value);
  }

  private getFallbackFromStore(store: FaqStore): FaqDetail {
    return store.detailsById['1'] ?? this.seedDetailsById['1'];
  }

  private buildGeneratedStore(): FaqStore {
    const drafts = this.generationTemplates.map((template, index) => {
      const id = String(index + 1);
      const confidence = 70 + Math.floor(Math.random() * 29);
      const status: DraftStatus = 'Draft';

      return {
        id,
        title: template.title,
        intent: template.intent,
        family: template.family,
        status,
        confidence,
        caseCount: template.caseCount,
        updated: 'Just now'
      };
    });

    const detailsById = drafts.reduce<Record<string, FaqDetail>>((acc, draft) => {
      acc[draft.id] = this.buildDetailFromDraft(draft);
      return acc;
    }, {});

    return {
      drafts,
      detailsById
    };
  }

  private buildDetailFromDraft(draft: FaqDraft): FaqDetail {
    return {
      id: draft.id,
      intent: draft.intent,
      updated: draft.updated,
      family: draft.family,
      status: draft.status,
      reviewNeeded: true,
      title: draft.title,
      confidence: draft.confidence,
      caseCount: draft.caseCount,
      problemStatement: `Users are reporting recurring issues related to "${draft.title}" in recent support interactions.`,
      causeExplanation:
        'Initial clustering suggests process ambiguity and inconsistent system feedback as the primary drivers for this issue family.',
      steps: [
        'Validate the user context and account state before troubleshooting.',
        'Apply the recommended resolution checklist and confirm expected behavior.',
        'Escalate only when the issue persists after standard remediation.'
      ],
      edgeCases: [
        'Legacy accounts created before current policy rollout',
        'Region-specific compliance constraints',
        'Enterprise tenant custom settings'
      ],
      contactSupport:
        'Escalate to Tier 2 with screenshots, timestamps, and account identifier if unresolved after checklist completion.',
      evidence: [
        {
          id: `#${4900 + draft.id}`,
          source: 'Email',
          summary: `Customer reports issue pattern matching ${draft.family.toLowerCase()} family behavior.`,
          timeAgo: '1 hour ago'
        },
        {
          id: `#${4800 + draft.id}`,
          source: 'Chat',
          summary: `Agent notes repeated occurrences of ${draft.title.toLowerCase()}.`,
          timeAgo: '3 hours ago'
        }
      ]
    };
  }


}
