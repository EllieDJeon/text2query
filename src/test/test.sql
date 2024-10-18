WITH credit_aggr AS(
SELECT
    user_id,
    MAX(insert_time) insert_time
FROM lms.kcb_summ_info
WHERE DATE(insert_time) >= CURDATE()
GROUP BY 1
),

credit_recent AS( -- 7일내 최근 신용점수
SELECT
    lk.user_id,
    credit_score,
    lk.insert_time
FROM lms.kcb_summ_info lk
    INNER JOIN credit_aggr ca
    ON lk.user_id = ca.user_id
    AND lk.insert_time = ca.insert_time

WHERE DATE(lk.insert_time) >= CURDATE()

GROUP BY 1,2,3
),

base AS ( -- 한도조회 + 최근 신용점수
SELECT
    la.insert_time,
    la.user_id,
    ll.application_id,
    cr.credit_score,
    FLOOR(credit_score/20)*20 credit_div,
    CASE WHEN SUM(CASE WHEN ll.status IN ('contract_requested', 'contract_applied', 'contract_failed', 'contract_approved', 'contract_rejected', 'contract_retracted') THEN 1 ELSE 0 END) = 0 THEN 1 ELSE 0 END AS is_all_denied
FROM fcsdb.la_application la
INNER JOIN fcsdb.la_loanapply ll
    ON la.id = ll.application_id
#     AND DATE(la.insert_time) >= DATE('2024-09-19')
    AND DATE(la.insert_time) = CURDATE()
INNER JOIN credit_recent cr
    ON la.user_id = cr.user_id
INNER JOIN fcsdb.user3 u3
    ON la.user_id = u3.id
    AND u3.status IN ('enabled', 'dormant')
    AND DATE(u3.insert_time) = CURDATE()
GROUP BY 1,2,3,4,5
),

approve_per AS( -- 신용점수대별 승인률
SELECT
    credit_div,
    COUNT(DISTINCT CASE WHEN is_all_denied = 0 THEN application_id ELSE NULL END)*100.0/COUNT(DISTINCT application_id) approve_per
FROM base
GROUP BY 1
)

SELECT
    b.user_id,
    b.credit_score
    ap.approve_per
FROM base b
    INNER JOIN approve_per ap
    ON b.credit_div + 20 = ap.credit_div
WHERE DATE(insert_time) = CURDATE()
AND is_all_denied = 1