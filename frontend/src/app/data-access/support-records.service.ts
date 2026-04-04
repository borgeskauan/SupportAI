import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { map } from 'rxjs/operators';

import { API_ENDPOINTS } from './api-config';
import {
  BackendSupportRecordListResponse,
  SupportRecordListResponse,
  mapBackendToSupportRecord,
} from './support-record.models';

@Injectable({
  providedIn: 'root',
})
export class SupportRecordsService {
  constructor(private http: HttpClient) {}

  getRecords(): Observable<SupportRecordListResponse> {
    return this.http.get<BackendSupportRecordListResponse>(API_ENDPOINTS.records).pipe(
      map((response) => ({
        total: response.total,
        records: response.records.map(mapBackendToSupportRecord),
      }))
    );
  }
}
