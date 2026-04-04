import { Component, LOCALE_ID, computed, inject, signal } from '@angular/core';
import { toSignal } from '@angular/core/rxjs-interop';
import { RouterLink } from '@angular/router';
import { catchError, of, startWith, tap } from 'rxjs';

import { SupportRecordsService } from '../data-access/support-records.service';
import {
  SupportRecord,
  SupportRecordListResponse,
  localizeSupportRecordSentiment,
  localizeSupportRecordSeverity,
  localizeSupportRecordSource,
  localizeSupportRecordStatus,
} from '../data-access/support-record.models';

@Component({
  selector: 'app-support-records-list',
  imports: [RouterLink],
  templateUrl: './support-records-list.component.html',
  styleUrl: './support-records-list.component.css',
})
export class SupportRecordsListComponent {
  private readonly locale = inject(LOCALE_ID);
  private readonly supportRecords = inject(SupportRecordsService);

  protected readonly loadError = signal('');

  protected readonly recordsResponse = toSignal(
    this.supportRecords.getRecords().pipe(
      startWith(null as SupportRecordListResponse | null),
      tap(() => this.loadError.set('')),
      catchError(() => {
        this.loadError.set($localize`:@@records_error_loading:We couldn't load the support records right now.`);
        return of({
          total: 0,
          records: [],
        } satisfies SupportRecordListResponse);
      })
    )
  );

  protected readonly totalCount = computed(() => this.recordsResponse()?.total ?? 0);

  protected readonly records = computed(() => {
    const response = this.recordsResponse();
    if (!response) {
      return [] as SupportRecord[];
    }

    return [...response.records].sort((left, right) => {
      return Date.parse(right.createdAt) - Date.parse(left.createdAt);
    });
  });

  protected readonly resolvedCount = computed(() => {
    return this.records().filter((record) => record.status.toLowerCase() === 'resolved').length;
  });

  protected readonly productAreaCount = computed(() => {
    return new Set(this.records().map((record) => record.productArea)).size;
  });

  protected readonly hasLoaded = computed(() => this.recordsResponse() !== null);

  protected formatCreatedAt(value: string): string {
    try {
      return new Intl.DateTimeFormat(this.locale, {
        dateStyle: 'medium',
        timeStyle: 'short',
      }).format(new Date(value));
    } catch {
      return value;
    }
  }

  protected sourceLabel(sourceType: string): string {
    return localizeSupportRecordSource(sourceType);
  }

  protected statusLabel(status: string): string {
    return localizeSupportRecordStatus(status);
  }

  protected severityLabel(severity: string): string {
    return localizeSupportRecordSeverity(severity);
  }

  protected sentimentLabel(sentiment: string): string {
    return localizeSupportRecordSentiment(sentiment);
  }

  protected cssToken(value: string): string {
    return value.toLowerCase().replace(/[^a-z0-9]+/g, '-');
  }
}
