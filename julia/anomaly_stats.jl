# ── AIRA Julia Anomaly Statistics Engine ──
# Statistical anomaly detection for identity behaviour.
# Uses Julia's speed for real-time analysis of large event streams.

module AnomalyStats

export detect_statistical_anomaly, compute_baseline, zscore_anomalies

"""
Compute a baseline profile from historical behaviour data.
Returns mean and standard deviation for each metric.
"""
function compute_baseline(
    historical_data::Matrix{Float64}
)::Tuple{Vector{Float64}, Vector{Float64}}

    n_metrics = size(historical_data, 2)
    means     = zeros(Float64, n_metrics)
    stds      = zeros(Float64, n_metrics)

    for metric in 1:n_metrics
        col          = historical_data[:, metric]
        means[metric] = sum(col) / length(col)
        variance      = sum((col .- means[metric]).^2) / length(col)
        stds[metric]  = sqrt(variance)
    end

    return means, stds
end

"""
Detect anomalies using Z-score method.
Returns anomaly score (0-100) and which metrics are anomalous.
"""
function zscore_anomalies(
    current_values::Vector{Float64},
    baseline_means::Vector{Float64},
    baseline_stds::Vector{Float64},
    threshold::Float64 = 2.5
)::Tuple{Float64, Vector{Bool}}

    n_metrics      = length(current_values)
    anomalous      = Vector{Bool}(undef, n_metrics)
    total_zscore   = 0.0
    anomaly_count  = 0

    for i in 1:n_metrics
        std = baseline_stds[i] == 0.0 ? 1.0 : baseline_stds[i]
        z   = abs((current_values[i] - baseline_means[i]) / std)
        anomalous[i] = z > threshold
        if anomalous[i]
            total_zscore += z
            anomaly_count += 1
        end
    end

    # Anomaly score: proportion of anomalous metrics x severity
    base_score    = (anomaly_count / n_metrics) * 100.0
    severity_mult = anomaly_count > 0 ? (total_zscore / anomaly_count) / threshold : 1.0
    anomaly_score = clamp(base_score * severity_mult, 0.0, 100.0)

    return anomaly_score, anomalous
end

"""
Detect statistical anomaly for a single identity.
Returns anomaly score and detailed breakdown.
"""
function detect_statistical_anomaly(
    current_values::Vector{Float64},
    baseline_means::Vector{Float64},
    baseline_stds::Vector{Float64},
    metric_names::Vector{String}
)::Dict{String, Any}

    score, anomalous = zscore_anomalies(
        current_values,
        baseline_means,
        baseline_stds
    )

    anomalous_metrics = String[]
    for (i, is_anomalous) in enumerate(anomalous)
        if is_anomalous && i <= length(metric_names)
            push!(anomalous_metrics, metric_names[i])
        end
    end

    level = if score >= 80 "critical"
            elseif score >= 60 "high"
            elseif score >= 40 "medium"
            else "low" end

    return Dict{String, Any}(
        "anomaly_score"     => round(score, digits=2),
        "anomaly_level"     => level,
        "anomalous_metrics" => anomalous_metrics,
        "total_metrics"     => length(metric_names),
        "anomalous_count"   => length(anomalous_metrics)
    )
end

"""
Batch anomaly detection for multiple identities simultaneously.
"""
function batch_anomaly_detection(
    all_current::Matrix{Float64},
    baseline_means::Vector{Float64},
    baseline_stds::Vector{Float64}
)::Vector{Float64}

    n_identities  = size(all_current, 1)
    anomaly_scores = zeros(Float64, n_identities)

    Threads.@threads for i in 1:n_identities
        score, _ = zscore_anomalies(
            all_current[i, :],
            baseline_means,
            baseline_stds
        )
        anomaly_scores[i] = score
    end

    return anomaly_scores
end

end # module
