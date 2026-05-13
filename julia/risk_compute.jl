# ── AIRA Julia Risk Compute Engine ──
# High-speed risk scoring using Julia's numerical performance.
# Called from Python via julia_bridge.py

module RiskCompute

export compute_risk_score, batch_risk_scores, compute_risk_matrix

"""
Compute a single identity risk score from weighted features.
Returns a score between 0 and 100.
"""
function compute_risk_score(features::Dict{String, Float64})::Float64
    weights = Dict(
        "failed_logins"          => 15.0,
        "off_hours_access"       => 10.0,
        "sensitive_data_access"  => 20.0,
        "new_device"             => 8.0,
        "location_anomaly"       => 12.0,
        "privilege_escalation"   => 25.0,
        "data_exfiltration"      => 30.0,
        "lateral_movement"       => 20.0,
        "credential_sharing"     => 18.0,
        "policy_violation"       => 15.0,
    )

    score = 0.0
    max_possible = sum(values(weights))

    for (feature, value) in features
        weight = get(weights, feature, 5.0)
        score += weight * clamp(value, 0.0, 1.0)
    end

    return clamp((score / max_possible) * 100.0, 0.0, 100.0)
end

"""
Compute risk scores for a batch of identities in parallel.
Much faster than Python for large identity sets.
"""
function batch_risk_scores(
    identity_ids::Vector{String},
    feature_sets::Vector{Dict{String, Float64}}
)::Vector{Dict{String, Any}}

    results = Vector{Dict{String, Any}}(undef, length(identity_ids))

    Threads.@threads for i in 1:length(identity_ids)
        score = compute_risk_score(feature_sets[i])
        level = if score >= 80 "critical"
                elseif score >= 60 "high"
                elseif score >= 40 "medium"
                else "low" end

        results[i] = Dict(
            "identity_id" => identity_ids[i],
            "risk_score"  => round(score, digits=2),
            "risk_level"  => level
        )
    end

    return results
end

"""
Compute a full risk matrix for a sector.
Returns a matrix of identity x framework risk scores.
"""
function compute_risk_matrix(
    n_identities::Int,
    n_frameworks::Int,
    base_scores::Matrix{Float64}
)::Matrix{Float64}

    risk_matrix = similar(base_scores)

    for i in 1:n_identities
        for j in 1:n_frameworks
            # Apply sector adjustment factor
            adjustment = 1.0 + (rand() * 0.2 - 0.1)
            risk_matrix[i, j] = clamp(base_scores[i, j] * adjustment, 0.0, 100.0)
        end
    end

    return risk_matrix
end

end # module
